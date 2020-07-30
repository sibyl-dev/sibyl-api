import React from 'react';
import '../../assets/sass/dash-wrapper.scss';

const DashWrapper = (props) => (
  <div className={`dash-wrapper ${props.className}`}>
    <div className="dash-body">{props.children}</div>
  </div>
);

export default DashWrapper;
