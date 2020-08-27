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
    grouppedFeatures: {
      negativeFeaturesContrib: {
        PRI_PRNT_AGE_2024_COUNT: 2,
        category: 'demographics',
        contributionValue: -0.43298241559380907,
        description: 'Counts of the number of parents that are 20<=age<25',
        name: 'PRI_PRNT_AGE_2024_COUNT',
        type: 'numeric',
      },
      positiveFeaturesContrib: {
        PRI_FOCUS_AGE_TOD: 1,
        category: 'demographics',
        contributionValue: 0.17053285540215513,
        description: 'Child in focus is between the ages of 1 and 3 at time of referral',
        name: 'PRI_FOCUS_AGE_TOD',
        type: 'binary',
      },
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
