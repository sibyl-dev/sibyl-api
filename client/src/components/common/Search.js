import React from 'react';
import Autocomplete from '@material-ui/lab/Autocomplete';
import parse from 'autosuggest-highlight/parse';
import match from 'autosuggest-highlight/match';

import './styles/Search.scss';

const SearchComponent = ({ hayStack, placeholder }) => (
  <div className="search-wrapper">
    <Autocomplete
      id="highlights-demo"
      options={hayStack}
      getOptionLabel={(option) => option.feature}
      disablePortal={true}
      renderInput={(params) => (
        <div ref={params.InputProps.ref}>
          <input type="text" {...params.inputProps} placeholder={placeholder} />
        </div>
      )}
      renderOption={(option, { inputValue }) => {
        const matches = match(option.feature, inputValue);
        const parts = parse(option.feature, matches);

        return (
          <div>
            {parts.map((part, index) => (
              <span key={index} style={{ fontWeight: part.highlight ? 700 : 400 }}>
                {part.text}
              </span>
            ))}
          </div>
        );
      }}
    />
  </div>
);

SearchComponent.defaultProps = {
  placeholder: 'Search feature',
};

export default SearchComponent;
