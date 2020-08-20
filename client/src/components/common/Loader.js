import React from 'react';
import '../../assets/sass/loader.scss';
import { LoaderIcon } from '../../assets/icons/icons';

const Loader = (props) => {
  const { isLoading, children, colSpan, minHeight } = props;
  const tblLoader = (
    <tr className="table-loader">
      <td colSpan={colSpan}>
        <div className="loader" style={{ minHeight: `${minHeight}px` }}>
          <div className="loading-text">
            <LoaderIcon />
          </div>
        </div>
      </td>
    </tr>
  );

  return isLoading ? tblLoader : children;
};

Loader.defaultProps = {
  minHeight: 500,
  colSpan: 4,
};

export default Loader;
