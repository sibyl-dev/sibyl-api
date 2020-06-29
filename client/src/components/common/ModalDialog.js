import React from 'react';
import { Modal } from 'react-bootstrap';
import '../../assets/sass/modal.scss';

const ModalDialog = ({ isOpen, title, children, onClose, className }) => (
  <Modal show={isOpen} centered onHide={onClose} className={className}>
    <Modal.Header closeButton>{title}</Modal.Header>
    <Modal.Body>{children}</Modal.Body>
  </Modal>
);
export default ModalDialog;
