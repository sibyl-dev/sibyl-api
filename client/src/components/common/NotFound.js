import React, { Component } from 'react';
import DashWrapper from './DashWrapper';
import { setActivePageAction } from '../../model/actions/sidebar';
import { connect } from 'react-redux';

class NotFound extends Component {
  componentDidMount() {
    this.props.setActivePage('Not found');
  }
  render() {
    return (
      <div className="component-wrapper">
        <DashWrapper>
          <div className="info">
            <p>Sorry. We didn't found what you're looking for</p>
          </div>
        </DashWrapper>
      </div>
    );
  }
}

export default connect(null, (dispatch) => ({
  setActivePage: (pageName) => dispatch(setActivePageAction(pageName)),
}))(NotFound);
