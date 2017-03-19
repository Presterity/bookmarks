/** @jsx h */

import { Component, h, render } from 'preact';

export default class BookmarkList extends Component {

  render(props) {
    const rows = props.bookmarks.map(bookmark => (
      <tr id={bookmark.bookmark_id}>
        <td>{bookmark.summary}</td>
        <td>
          <a href={bookmark.url} target="_blank">{bookmark.tld}</a>
        </td>
      </tr>
    ));
    return (
      <table>
        {rows}
      </table>
    );
  }

}
