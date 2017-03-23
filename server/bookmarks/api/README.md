# Bookmark Manager REST API

This document describes the REST API for the bookmark manager

## API versioning

The API URIs will include a version in the form of yymm. This is concise, human friendly, and continuously increasing. 
If we ever really mess up and need to make two backwards incompatible changes to an API in the same month, we can just 
fudge it by jumping forward a month. The initial version of the API is 1702.

## HTTP headers

TODO expected HTTP headers, e.g., how to authenticate with this API -- OAuth2?

## Error codes

TODO general comments about error codes coming from the API. Document HTTP-level error codes that might be expected.
Each API may have additional application-level error codes in the response body.

## Bookmark CRUD

A bookmark resource is identified by a UUID and contains the following attributes:

- `bookmark_id` the UUID of the bookmark, which can be used to identify it in various REST calls
- `url` the url of referenced article
- `summary` user-supplied summary of article
- `description` user-supplied description or excerpt of article, usually longer and more detailed than the summary
- `display_date` the date of event that is the topic of the article to be used for sorting in a timeline. The date
should be as specific as possible. Valid formats are: `%Y.%m.%d %H:%M` (e.g., `2017.03.17 09:23`), `%Y.%m.%d %H`, 
`%Y.%m.%d`, `%Y.%m`, `%Y`.
- `status` the status of bookmark; e.g. 'not relevant', 'duplicate', 'accepted', etc.
- `source` object containing information about the source of the bookmark
- `submission` object containing information about the bookmark submission 
- `topics` the topics associated with bookmark; bookmark will appear in timeline on these topic pages
- `notes` volunteer or application-specified notes on bookmark; e.g., "duplicate of bookmark id 567" 

A source object can contain the following fields:
- `name` the name of the source, e.g., 'raindrop'
- `item_id` the external identifier of the bookmark given by the source
- `last_updated` the last date the bookmark was updated from its source; used to decide if bookmark needs to be 
refreshed in data store

A submission object can contain the following fields:
- `submitter_id` identifier of the person who submitted bookmark; might be email, Twitter handle, or something else

### Get bookmark

Bookmarks are retrieved by their UUID, which is put in the placeholder `<bookmark_id>`
 
`GET /api/<version>/bookmarks/<bookmark_id>`

The response body will contain JSON that looks like this:

```
{
  "bookmark_id" : <str>,
  "description" : <str>,
  "display_date": <str that is date for display, e.g. '2017.01'>,
  "summary"     : <str>,
  "sort_date"   : <str that is utc date in isoformat>,
  "status"      : <str>,
  "topics"      : [<str>, ...],
  "tld"         : <str that is top-level domain, e.g. 'cnn.com'>,
  "url"         : <str>
}
```

### Create bookmark

`POST /api/<version>/bookmarks/`

The JSON post body contains bookmark fields to be inserted into the DB. The service will assign a UUID which will be 
given back in the response. The expected format is the following. A question mark (`?`) after a field means that the 
field is optional. All other fields are required.

```
{
  "url"         : <str>,
  "summary"     : <str>,
  "display_date": <str>,  
  "description" : <str>?,
  "status"      : <str>?,
  "source"      : {
    "name"        : <str>?,
    "item_id"     : <str>?,
    "last_updated": <str>?
  }?,
  "submission"  : {
    "submitter_id"       : <str>?
  }?
  "topics"             : [<str>, ...]?,
  "notes"              : [<str>, ...]?,
```


### Update a bookmark

`PUT /api/<version>/bookmarks/<bookmark_id>`

The fields in the request body will overwrite the corresponding database fields for the bookmark. Fields omitted will
be left unchanged. The request format matches that of create, except some fields are not allowed. Allowed fields
are `url`, `summary`, `display_date`, `description`, `status`, `source`, `submission`. To update topics and notes, 
see their APIs.

### Delete a bookmark

`DELETE /api/<version>/bookmarks/<bookmark_id>`


### Get notes for a bookmark

`GET /api/<version>/bookmarks/<bookmark_id>/notes/`

Get all notes for a bookmark. The response body looks like this:

```
{
  "bookmark_id": <str>,
  "notes": [
    {
       "note_id": <str>,
       "text"   : <str>
    }, 
    ...
    ]
}
```


### Add notes to a bookmark

`POST /api/<version>/bookmarks/<bookmark_id>/notes/`

The request body looks like this:

```
{
  "notes": [<str>, ...]
}
```

When the above request is made, each of the specified notes are assigned a UUID and added to the bookmark. The response
includes the UUID for each note.

### Remove a note from a bookmark

`DELETE /api/<version>/notes/<note_id>`

When the above request is made, the specified note is removed from the bookmark.

### Edit a note on a bookmark

`PUT /api/<version>/notes/<note_id>`

The request body looks like this:

```
{
  "text": <str>
}
```

When the above request is made, the text of the note is replaced by the specified text.
