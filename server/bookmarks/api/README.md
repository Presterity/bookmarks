# Bookmark Manager REST API

This document describes the REST API for managing bookmarks.

## API Clients

The Bookmark Manager APIs will be called from the presterity.org website to produce the timeline section of each topic 
page and from the internal Bookmark Manager tool.

## API versioning

The API URIs will include a version in the form of `<yymm>`. This is concise, human friendly, and continuously increasing. 
If we ever really mess up and need to make two backwards incompatible changes to an API in the same month, we can just 
fudge it by jumping forward a month. The initial version of the API is 1702.

## HTTP headers

Requests that have a JSON body must be accompanied by a `Content-Type application/json` header.

## HTTP status codes

Common HTTP status codes return by this API are:

| status code | action             | description |
|-------------|--------------------|-------------|
| 200         | N/A                | ok          |
| 204         | N/A                | no content or empty results set|
| 400         | none               | the request isn't formatted correctly or contains invalid content. Indicates a client-side misuse of an API that should be fixed.|
| 401         | obtain credentials | client is not authenticated or authorized to access the resource. Obtain valid credentials before re-trying.|
| 404         | none               | the requested a resource was not found (e.g., no bookmark with a given ID)|
| 500         | none               | the request triggered a bug in the server. Don't retry.|
| 503         | retry              | server is temporarily unavailable. Retry the request (see retries)|

### 503 retries

TBD - retry behavior when 503 is received by the client

## UUIDs

Individual resources (such as bookmarks) are identified by UUIDs. We use version 4 RFC 4122 identifiers consisting
 of 32 hexadecimal digits interspersed with 4 dashes. For detailed information about these UUIDs and how they are
 generated, see the [python UUID docs](https://docs.python.org/3.6/library/uuid.html).

## Bookmarks

A bookmark resource is identified by a UUID and contains the following attributes:

- `bookmark_id` the UUID of the bookmark, which can be used to identify it in various REST calls
- `url` the url of referenced article (e.g., 'cnn.com')
- `tld` the top-level domain of the URL
- `summary` user-supplied summary of article
- `description` user-supplied description or excerpt of article, usually longer and more detailed than the summary
- `display_date` the date of event that is the topic of the article to be used for sorting in a timeline. The date
should be as specific as possible. Valid formats are: `%Y.%m.%d %H:%M` (e.g., `2017.03.17 09:23`), `%Y.%m.%d %H`, 
`%Y.%m.%d`, `%Y.%m`, `%Y`.
- `status` the status of bookmark; e.g. 'new', 'submitted', 'accepted', etc.
- `topics` the topics associated with bookmark; bookmark will appear in timeline on these topic pages
- `notes` volunteer or application-specified notes on bookmark; e.g., "duplicate of bookmark id 567" 

## Get bookmarks APIs

To populate timelines on presterity.org topic pages, bookmarks must be queryable by topic and ordered by date. To 
support a potential overall timeline, the bookmarks must be queryable by date range. 

Paging is supported for all query APIs that return multiple bookmarks. Paging is implemented using cursors, 
strings that are opaque to the client and that the server can interpret to use in a SELECT statement for an ordered 
query to pick up where the previous result set left off.

### GET bookmark by UUID

Retrieves one bookmark, by its UUID, which is put in the placeholder `<bookmark_id>`
 
`GET /api/<yymm>/bookmarks/<bookmark_id>`

The response body will contain JSON that looks like this:

```
{
  "bookmark_id" : <str>,
  "description" : <str>,
  "display_date": <str>,
  "summary"     : <str>,
  "status"      : <str>,
  "topics"      : [<str>, ...],
  "tld"         : <str>,
  "url"         : <str>
}
```

This endpoint returns status code 404 if there is no bookmark with the UUID provided.

### GET bookmarks by topic

Retrieves all bookmarks with at least one of a list of topics. If no topics are provided, all bookmarks are returned.

`GET /api/<yymm>/bookmarks/?topic=<topic1>&topic=<topic2>&...`

Optional query arguments:

* one or more topic=<topic> arguments where topic is the name of a presterity.org topic page
* count=<int> where count is the maximum number of results to return; a default max will be enforced
* cursor=<string> where the string is a token provided in the previous response

Response status codes:

* 200 OK: bookmarks found and returned
* 204 No Content: no bookmarks found

Response JSON:

```
{
  "bookmarks"  : [<Bookmark JSON>, …]  # ordered ascending by sort_date
  "total_count": <int>
  "next_cursor": <string>
}
```

### GET bookmarks by date range

`GET /api/1702/bookmarks/?start=<yymmdd>`

Optional query arguments:

* end=<yyyymmdd> to specify the end of the date range
* count=<int> where count is the maximum number of results to return; a default max will be enforced
* cursor=<string> where the string is a token provided in the previous response

Response status codes:

* 200 OK: bookmarks found and returned
* 204 No Content: no bookmarks found

Response JSON:

```
{
  "bookmarks"  : [<Bookmark JSON>, …]  # ordered ascending by sort_date
  "total_count": <int>
  "next_cursor": <string>
}
```

## Create, Update and Delete APIs

A new bookmark may be created by a PUT operation, if a UUID for the bookmarks is specified, or by a POST operation, 
if the id is to be assigned by the server. Bookmark updates are always PUT operations. Bookmarks are deleted using DELETE.

### Create bookmark

`POST /api/<yymm>/bookmarks/`

The JSON post body contains information about a new bookmark that is added to the database. The expected format of the
POST body is the following. A question mark (`?`) after a field means that the field is optional. All other fields are 
required.

```
{
  "url"         : <str>,
  "summary"     : <str>,
  "display_date": <str>,  
  "description" : <str>?,
  "topics"      : [<str>, ...]?,
```


### Update a bookmark, or create with pre-determined UUID

`PUT /api/<yymm>/bookmarks/<bookmark_id>`

The fields in the request body will overwrite the corresponding database fields for the bookmark. Fields omitted will
be left unchanged. Fields provided that are empty or blank will unset corresponding database fields. The request format 
matches that of POST, except that when updating an existing bookmark, all fields are optional.

### Delete a bookmark

`DELETE /api/<yymm>/bookmarks/<bookmark_id>`

Since the intent of the DELETE is to remove the bookmark, the service responds with status code 204 whether the
`<bookmark_id>` exists at the time of the request or not.

## Notes APIs

Notes contain free-form, supplementary information about bookmarks visible only to the Presterity team. These APIs can
add, remove or update notes on a bookmark.

_**Note: these APIs are not implemented yet**_

### Get notes for a bookmark

`GET /api/<yymm>/bookmarks/<bookmark_id>/notes/`

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

`POST /api/<yymm>/bookmarks/<bookmark_id>/notes/`

The request body looks like this:

```
{
  "notes": [<str>, ...]
}
```

When the above request is made, each of the specified notes are assigned a UUID and added to the bookmark. The response
includes the UUID for each note.

### Remove a note from a bookmark

`DELETE /api/<yymm>/notes/<note_id>`

When the above request is made, the specified note is removed from the bookmark.

### Edit a note on a bookmark

`PUT /api/<yymm>/notes/<note_id>`

The request body looks like this:

```
{
  "text": <str>
}
```

When the above request is made, the text of the note is replaced by the specified text.
