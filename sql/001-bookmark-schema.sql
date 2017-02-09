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
DROP TABLE IF EXISTS apps.bookmarks CASCADE;
CREATE TABLE apps.bookmarks (

  -- bookmark_id is UUID stored as 8-4-4-4-12
  bookmark_id CHAR(36) NOT NULL PRIMARY KEY,

  -- url of referenced article
  url VARCHAR(2000) NOT NULL,

  -- user-supplied summary of article
  summary TEXT NOT NULL,

  -- user-supplied description or excerpt of article
  description TEXT DEFAULT NULL,

  -- datetime of event that is topic of article to be used for sorting; may not
  -- be exact event_date, i.e., we may only know year & month, in which case we
  -- will store the first of the month and sort by that, but only display the 
  -- actual provided information, using display_date_format 
  sort_date TIMESTAMPTZ NOT NULL,
  
  -- status of bookmark; e.g. 'not relevant', 'duplicate', 'accepted', etc.
  status VARCHAR(100) DEFAULT NULL,

  -- format for date that will be displayed with bookmark: %Y, %Y.%m, %Y.%m.%d, %Y.%m.%d %H, %Y.%m.%d %H:%M
  display_date_format VARCHAR(20) NOT NULL,

  -- source of bookmark, e.g. 'raindrop'
  source VARCHAR(50) DEFAULT NULL,

  -- identifier of bookmark by source, e.g. raindrop_id 
  source_item_id VARCHAR(100) DEFAULT NULL,
  
  -- last_updated date on source; used to decide if bookmark needs to be refreshed in data store
  source_last_updated TIMESTAMPTZ DEFAULT NULL,

  -- id of person who submitted bookmark; might be email, Twitter handle, or something else
  submitter_id VARCHAR(100) DEFAULT NULL,
  
  -- date on which bookmark was submitted
  submission_date TIMESTAMPTZ DEFAULT NULL,

  -- for ops only
  audit_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
  audit_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE TRIGGER BOOKMARKS_AUDIT_UPDATED BEFORE UPDATE ON apps.bookmarks 
FOR EACH ROW EXECUTE PROCEDURE set_audit_updated();


-- Topics associated with bookmark; bookmark will appear in timeline on these topic pages
DROP TABLE IF EXISTS apps.bookmark_topics CASCADE;
CREATE TABLE apps.bookmark_topics (
  bookmark_id CHAR(36) NOT NULL,
  topic VARCHAR(100) NOT NULL,

  -- date available for business logic
  created_on TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,

  -- for ops only
  audit_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
  audit_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,

  PRIMARY KEY (bookmark_id, topic),
  FOREIGN KEY (bookmark_id) REFERENCES apps.bookmarks
);
CREATE INDEX BOOKMARK_TOPICS_TOPIC_IDX ON apps.bookmark_topics USING btree (topic);
CREATE TRIGGER BOOKMARK_TOPICS_AUDIT_UPDATED BEFORE UPDATE ON apps.bookmark_topics 
FOR EACH ROW EXECUTE PROCEDURE set_audit_updated();


-- Volunteer or application-specified notes on bookmark; i.e. "duplicate of bookmark id 567"
DROP TABLE IF EXISTS apps.bookmark_notes CASCADE;
CREATE TABLE apps.bookmark_notes (
  note_id CHAR(36) NOT NULL PRIMARY KEY,
  bookmark_id CHAR(36) NOT NULL,
  text TEXT NOT NULL,

  -- id of voluteer or application who authored note
  author VARCHAR(100) NOT NULL,

  -- date available for business logic
  created_on TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,

  -- For ops only
  audit_created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
  audit_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,

  FOREIGN KEY (bookmark_id) REFERENCES apps.bookmarks
);
CREATE INDEX BOOKMARK_NOTES_BOOKMARK_ID_IDX ON apps.bookmark_notes USING btree (bookmark_id);
CREATE TRIGGER BOOKMARK_NOTES_AUDIT_UPDATED BEFORE UPDATE ON apps.bookmark_notes
FOR EACH ROW EXECUTE PROCEDURE set_audit_updated();

