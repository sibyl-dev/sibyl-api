import React from 'react';
import '../../assets/sass/dash-wrapper.scss';

export const DashWrapper = (props) => {
  return (
    <div className={`dash-wrapper ${props.className}`}>
      <div className="dash-body">{props.children}</div>
    </div>
  );
};

export default DashWrapper;
