import React from 'react';
import { connect } from 'react-redux';
// import Autocomplete from '@material-ui/lab/Autocomplete';
// import parse from 'autosuggest-highlight/parse';
// import match from 'autosuggest-highlight/match';
import { CloseIncon } from '../../assets/icons/icons';

import './styles/Search.scss';
import { getFeaturesData, getIsFeaturesLoading, getFeaturesFilterCriteria } from '../../model/selectors/features';
import { setFilterCriteriaAction } from '../../model/actions/features';

// @TODO - remove in case actual search is accepted, imports as well
// const SearchComponent = (props) => {
//   const { hayStack, placeholder, features } = props;
//   const { processedFeatures } = features;
//   console.log(processedFeatures);
//   return (
//     <div className="search-wrapper">
//       <Autocomplete
//         id="highlights-demo"
//         options={hayStack}
//         getOptionLabel={(option) => option.feature}
//         renderInput={(params) => (
//           <div ref={params.InputProps.ref}>
//             <input type="text" {...params.inputProps} placeholder={placeholder} />
//           </div>
//         )}
//         renderOption={(option, { inputValue }) => {
//           const matches = match(option.feature, inputValue);
//           const parts = parse(option.feature, matches);

//           return (
//             <div>
//               {parts.map((part, index) => (
//                 <span key={index} style={{ fontWeight: part.highlight ? 700 : 400 }}>
//                   {part.text}
//                 </span>
//               ))}
//             </div>
//           );
//         }}
//       />
//     </div>
//   );
// };

const SearchComponent = (props) => {
  const { isFeaturesLoading, placeholder, currentFilterCriteria, setFilterCriteria } = props;
  return (
    <div className="search-field">
      <ul>
        <li>
          <input
            type="text"
            disabled={isFeaturesLoading}
            placeholder={placeholder}
            value={currentFilterCriteria}
            onChange={(event) => setFilterCriteria(event.target.value)}
          />
        </li>
        <li className={currentFilterCriteria ? 'visible' : ''}>
          <button type="button" onClick={() => setFilterCriteria('')}>
            <CloseIncon />
          </button>
        </li>
      </ul>
    </div>
  );
};

SearchComponent.defaultProps = {
  placeholder: 'Search feature',
};

export default connect(
  (state) => ({
    features: getFeaturesData(state),
    isFeaturesLoading: getIsFeaturesLoading(state),
    currentFilterCriteria: getFeaturesFilterCriteria(state),
  }),
  (dispatch) => ({
    setFilterCriteria: (filterValue) => dispatch(setFilterCriteriaAction(filterValue)),
  }),
)(SearchComponent);
