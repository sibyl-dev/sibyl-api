import React, { Component } from 'react';
import { connect } from 'react-redux';
import DashWrapper from './DashWrapper';
import { setActivePageAction } from '../../model/actions/sidebar';

class NotFound extends Component {
  componentDidMount() {
    this.props.setActivePage('Not found');
  }

  render() {
    return (
      <div className="component-wrapper">
        <DashWrapper>
          <div className="info">
            <p>Sorry. We didn&apos;t found what you&apos;re looking for</p>
          </div>
        </DashWrapper>
      </div>
    );
  }
}

export default connect(null, (dispatch) => ({
  setActivePage: (pageName) => dispatch(setActivePageAction(pageName)),
}))(NotFound);
