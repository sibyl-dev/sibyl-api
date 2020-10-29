import React from 'react';
import Select from 'react-select';
import './styles/Form.scss';

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
  const { options, onChange, value, disabled = false } = props;
  const catOptions = [];

  options.map((currentOption) =>
    catOptions.push({
      value: currentOption.name,
      label: currentOption.name,
      icon: currentOption.color,
      isFixed: true,
    }),
  );

  return (
    <Select
      isSearchable={false}
      isMulti
      classNamePrefix="sibyl-select"
      className="sibyl-select"
      formatOptionLabel={categoryFormatOptions}
      options={catOptions}
      isDisabled={disabled}
      placeholder="Category"
      onChange={onChange}
      value={value !== null && catOptions.filter((currentOpts) => value.indexOf(currentOpts.value) !== -1)}
    />
  );
};

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
