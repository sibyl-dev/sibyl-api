import React from 'react';
import Select from 'react-select';
import './styles/Form.scss';

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
        <i className="bullet" style={{ background: icon }} /> {label}
      </div>
    ) : (
      label
    )}
  </div>
);

export const CategorySelect = (props) => {
  const { options, onChange, value } = props;
  const catOptions = [];

  options.map((currentOption) => {
    catOptions.push({
      value: currentOption.name,
      label: currentOption.name,
      icon: currentOption.color,
      isFixed: true,
    });
  });

  return (
    <Select
      isSearchable={false}
      isMulti={true}
      classNamePrefix="sibyl-select"
      className="sibyl-select"
      formatOptionLabel={categoryFormatOptions}
      options={catOptions}
      placeholder="Category"
      onChange={onChange}
      value={value !== null && catOptions.filter((currentOpts) => value.indexOf(currentOpts.value) !== -1)}
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
