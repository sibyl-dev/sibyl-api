import React from 'react';
import { Details } from './Details';
import { renderWithStore, TestWrapper } from '../../tests/setup';
describe('Testing Details component -> ', () => {
  const store = {
    isEntityLoading: false,

    entityData: {
      contributions: {
        PRI_CBMS_FOCUS_CD_NOW: 0,
        PRI_CBMS_FOCUS_CD_1: 0,
      },
      features: {
        PRI_CBMS_FOCUS_CD_NOW: 0,
        PRI_CBMS_FOCUS_CD_1: 0,
      },
      featuresData: [
        {
          name: 'PRI_CBMS_FOCUS_CD_NOW',
          description: 'child in focus was receiving County Diversion (CD) benefits at time of referral.',
          category: 'program involvement',
          type: 'Boolean',
          importance: '-0.001859432',
        },
        {
          name: 'PRI_CBMS_FOCUS_CD_1',
          description:
            'child in focus received County Diversion (CD) benefits in the 1 year prior to referral, excl. clients who are actively receiving the service.',
          category: 'program involvement',
          type: 'Boolean',
          importance: '0',
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
