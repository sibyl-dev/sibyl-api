import React from 'react';
import { Details } from './Details';
import { renderWithStore, TestWrapper } from '../../tests/setup';

jest.mock('../common/Form', () => ({
  CategorySelect: () => 'Category select here',
}));

describe('Testing Details component -> ', () => {
  const store = {
    isEntityLoading: false,

    features: {
      processedFeatures: [
        {
          name: 'PRI_FOCUS_PLSM_PAST730_DUMMY',
          description: 'the child in focus had a child welfare placement in the last 730 days',
          type: 'binary',
          category: 'placement history',
          PRI_FOCUS_PLSM_PAST730_DUMMY: 1,
          contributionValue: 0.30542072380625584,
        },
        {
          name: 'PRI_CBMS_OTHC_CW_1_COUNT',
          description:
            'Count of other children in the referral (excl. child in focus) who received Colorado Works (CW) benefits in the 1 year prior to referral, excl. clients who are actively receiving the service.',
          type: 'binary',
          category: 'program involvement',
          PRI_CBMS_OTHC_CW_1_COUNT: 4,
          contributionValue: 0.24523142917914945,
        },
      ],
    },
    featureCategories: [
      { name: 'placement history', color: '#27ae60' },
      { name: 'program involvement', color: '#9e09b8' },
    ],
    entityData: {
      features: [
        {
          PRI_FOCUS_PLSM_PAST730_DUMMY: 1,
        },
      ],
    },
  };
  it('Should render without crashing', () => {
    const detailsComponent = renderWithStore(
      {},
      <TestWrapper>
        <Details {...store} />
      </TestWrapper>,
    );

    expect(detailsComponent).toMatchSnapshot();
  });
});
