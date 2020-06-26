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
  { value: 'All', label: 'All', isFixed: true },
  { value: 'True -> False', label: 'True -> False', isFixed: true },
  { value: 'False -> True', label: 'False -> True', isFixed: true },
  { value: 'Categorycal', label: 'Categorycal', isFixed: true },
  { value: 'Numerical', label: 'Numerical', isFixed: true },
];

const diffValues = [
  { value: 'Difference', label: 'Difference', isFixed: true },
  { value: 'Risk', label: 'Risk', isFixed: true },
  { value: 'Protective', label: 'Protective', isFixed: true },
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
      isMulti={true}
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
    placeholder="Changed Value"
  />
);

export const DiffSelect = () => (
  <Select
    isSearchable={false}
    isMulti={false}
    classNamePrefix="sibyl-select"
    className="sibyl-select"
    options={diffValues}
    placeholder="Difference"
  />
);
