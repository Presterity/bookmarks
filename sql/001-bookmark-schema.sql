/* Core bookmark schema */

-- Stored procedure for setting updated column
CREATE OR REPLACE FUNCTION set_audit_updated()
RETURNS TRIGGER AS ' 
BEGIN
    NEW.audit_updated = now();
    RETURN NEW; 
END;
' language 'plpgsql';

-- Main bookmark table
DROP TABLE IF EXISTS apps.bookmark CASCADE;
CREATE TABLE apps.bookmark (

  -- bookmark_id is UUID stored as 8-4-4-4-12
  bookmark_id CHAR(36) NOT NULL PRIMARY KEY,

  -- url of referenced article
  url VARCHAR(2000) NOT NULL,

  -- user-supplied summary of article
  summary TEXT NOT NULL,

  -- user-supplied description or excerpt of article
  description TEXT DEFAULT NULL,

  -- datetime of event that is topic of article
  sort_date_utc TIMESTAMPTZ NOT NULL,
  
  -- status of bookmark; e.g. 'not relevant', 'duplicate', 'accepted', etc.
  status VARCHAR(100) DEFAULT NULL,

  -- partial or full date that will be displayed with bookmark: YYYY, YYYY.mm, YYYY.mm.dd, YYYY.mm.dd HH, YYYY.mm.dd HH:MM
  display_date VARCHAR(50) NOT NULL,

  -- source of bookmark, e.g. 'raindrop'
  source VARCHAR(50) DEFAULT NULL,

  -- identifier of bookmark by source, e.g. raindrop_id 
  source_bookmark_id VARCHAR(100) DEFAULT NULL,
  
  -- last_updated date on source; used to decide if bookmark needs to be refreshed in data store
  source_last_updated TIMESTAMPTZ DEFAULT NULL,

  -- id of person who submitted bookmark; might be email, Twitter handle, or something else
  submitter_id VARCHAR(100) DEFAULT NULL,
  
  -- date on which bookmark was submitted
  submission_date_utc TIMESTAMPTZ DEFAULT NULL,

  -- for ops only
  audit_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
  audit_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE TRIGGER BOOKMARK_AUDIT_UPDATED BEFORE UPDATE ON apps.bookmark 
FOR EACH ROW EXECUTE PROCEDURE set_audit_updated();


-- Topics associated with bookmark; bookmark will appear in timeline on these topic pages
DROP TABLE IF EXISTS apps.bookmark_topic CASCADE;
CREATE TABLE apps.bookmark_topic (
  bookmark_id CHAR(36) NOT NULL,
  topic VARCHAR(100) NOT NULL,

  -- date available for business logic
  created_on TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,

  -- for ops only
  audit_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
  audit_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,

  PRIMARY KEY (bookmark_id, topic),
  FOREIGN KEY (bookmark_id) REFERENCES apps.bookmark
);
CREATE INDEX BOOKMARK_TOPIC_TOPIC_IDX ON apps.bookmark_topic USING btree (topic);
CREATE TRIGGER BOOKMARK_TOPIC_AUDIT_UPDATED BEFORE UPDATE ON apps.bookmark_topic 
FOR EACH ROW EXECUTE PROCEDURE set_audit_updated();


-- Volunteer or application-specified notes on bookmark; i.e. "duplicate of bookmark id 567"
DROP TABLE IF EXISTS apps.bookmark_note CASCADE;
CREATE TABLE apps.bookmark_note (
  note_id CHAR(36) NOT NULL PRIMARY KEY,
  bookmark_id CHAR(36) NOT NULL,
  note TEXT NOT NULL,

  -- id of voluteer or application who authored note
  author VARCHAR(100) NOT NULL,

  -- date available for business logic
  created_on TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,

  -- For ops only
  audit_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
  audit_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,

  FOREIGN KEY (bookmark_id) REFERENCES apps.bookmark
);
CREATE INDEX BOOKMARK_NOTE_BOOKMARK_ID_IDX ON apps.bookmark_note USING btree (bookmark_id);
CREATE TRIGGER BOOKMARK_NOTE_AUDIT_UPDATED BEFORE UPDATE ON apps.bookmark_note 
FOR EACH ROW EXECUTE PROCEDURE set_audit_updated();

