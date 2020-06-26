import React from 'react';
import '../../assets/sass/dash-wrapper.scss';
// import '../../assets/sass/dashWrapper';

export const DashWrapper = (props) => {
  return (
    <div className="dash-wrapper">
      <div className="dash-body">{props.children}</div>
    </div>
  );
};

export default DashWrapper;
