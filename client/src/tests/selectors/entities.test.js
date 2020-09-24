import {
  getActivePredictionScore,
  getCurrentEntityID,
  getCurrentUserID,
  getSelectedModelID,
} from '../../model/selectors/entities';

const defaultState = {
  entities: {
    entityID: '4a',
    models: [
      {
        id: '1',
      },
      {
        id: '2',
      },
      {
        id: '3',
      },
    ],
    userID: 'testID',
    predictionScore: 1.23,
    entityScore: 5.6,
  },
};

describe('Entities Selectors', () => {
  describe('getCurrentEntityID()', () => {
    it('returns the current entityID', () => {
      expect(getCurrentEntityID(defaultState)).toEqual('4a');
    });
    it('returns 0 because entityID is not set', () => {
      expect(getCurrentEntityID({ entities: { entityID: null } })).toEqual(0);
    });
  });
  describe('getSelectedModelID()', () => {
    it('returns the selected modelID', () => {
      expect(getSelectedModelID(defaultState)).toEqual('1');
    });
  });
  describe('getCurrentUserID()', () => {
    it('returns the currentUserID', () => {
      expect(getCurrentUserID(defaultState)).toEqual('testID');
    });
    it('returns `null` string because userID is not set', () => {
      expect(getCurrentUserID({ entities: { userID: null } })).toBeNull();
    });
  });
  describe('getActivePredictionScore()', () => {
    it('returns the prediction score', () => {
      expect(getActivePredictionScore(defaultState)).toEqual(1.23);
    });
    it('returns the entity score when prediction score is null', () => {
      const changedState = {
        entities: {
          predictionScore: null,
          entityScore: 5.6,
        },
      };

      expect(getActivePredictionScore(changedState)).toEqual(5.6);
    });
  });
});
