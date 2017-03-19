/** @jsx h */

import { Component, h, render } from 'preact';
import BookmarkList from './BookmarkList';

export default class Home extends Component {

  render(props) {
    return (
      <div>
        <h1>Presterity Bookmark Manager</h1>
        <BookmarkList bookmarks={props.bookmarks} />
      </div>
    );
  }

}
