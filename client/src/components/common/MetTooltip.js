import React from 'react';
import { OverlayTrigger, Tooltip } from 'react-bootstrap';
import '../../assets/sass/tooltip.scss';

const MetTooltip = (props) => (
  <OverlayTrigger placement={props.placement} overlay={<Tooltip id="tooltip">{props.title}</Tooltip>}>
    {props.children}
  </OverlayTrigger>
);

export default MetTooltip;
