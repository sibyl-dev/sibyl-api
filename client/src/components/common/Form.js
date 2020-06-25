import React from 'react';
import Select from 'react-select';
import './styles/Form.scss';

const categoryOptions = [
  { value: 'All', label: 'All', icon: 'all', isFixed: true },
  { value: 'Category 1', label: 'Category 1', icon: 'red', isFixed: true },
  { value: 'Category 2', label: 'Category 2', icon: 'blue', isFixed: true },
  { value: 'Category 3', label: 'Category 3', icon: 'green', isFixed: true },
  { value: 'Category 4', label: 'Category 4', icon: 'red', isFixed: true },
  { value: 'Category 5', label: 'Category 5', icon: 'orange', isFixed: true },
];

const valueSelect = [
  { value: 'True/False', label: 'True/False', isFixed: true },
  { value: 'Categorycal', label: 'Categorycal', isFixed: true },
  { value: 'Numerical', label: 'Numerical', isFixed: true },
];

const contribValues = [
  { value: 'Contrib 1', label: 'Contrib 1', isFixed: true },
  { value: 'Contrib 2', label: 'Contrib 2', isFixed: true },
  { value: 'Contrib 3', label: 'Contrib 3', icon: 'green', isFixed: true },
  { value: 'Contrib 4', label: 'Contrib 4', isFixed: true },
];

const categoryFormatOptions = ({ label, icon }) => (
  <div className="select-row">
    {icon !== 'all' ? (
      <div>
        <i className={`bullet ${icon}`} /> {label}{' '}
      </div>
    ) : (
      label
    )}
  </div>
);

export const CategorySelect = () => {
  return (
    <Select
      isSearchable={false}
      isMulti={false}
      classNamePrefix="sibyl-select"
      className="sibyl-select"
      formatOptionLabel={categoryFormatOptions}
      options={categoryOptions}
      placeholder="Category"
    />
  );
};

export const ValueSelect = () => (
  <Select
    isSearchable={false}
    isMulti={false}
    classNamePrefix="sibyl-select"
    className="sibyl-select"
    options={valueSelect}
    placeholder="Value"
  />
);

export const ContribSelect = () => (
  <Select
    isSearchable={false}
    isMulti={false}
    classNamePrefix="sibyl-select"
    className="sibyl-select"
    options={contribValues}
    placeholder="Value"
  />
);
