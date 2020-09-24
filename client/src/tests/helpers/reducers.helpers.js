export const generateTestsForPromiseReducers = (reducer, defaultState, promiseReducers) => {
  describe('Reducers triggered by actions with promise', () => {
    promiseReducers.forEach((promiseReducer) => {
      it(`${promiseReducer.name}_REQUEST`, () => {
        const requestAction = {
          type: `${promiseReducer.name}_REQUEST`,
        };
        expect(reducer(defaultState, requestAction)).toEqual({
          ...defaultState,
          [promiseReducer.loading]: true,
        });
      });

      it(`${promiseReducer.name}_SUCCESS`, () => {
        const fulfillAction = {
          type: `${promiseReducer.name}_SUCCESS`,
          ...promiseReducer.sendData,
        };
        expect(reducer(defaultState, fulfillAction)).toEqual({
          ...defaultState,
          [promiseReducer.loading]: false,
          [promiseReducer.key]: promiseReducer.testData,
        });
      });

      it(`${promiseReducer.name}_FAILURE`, () => {
        const requestAction = {
          type: `${promiseReducer.name}_FAILURE`,
        };
        expect(reducer(defaultState, requestAction)).toEqual({
          ...defaultState,
          [promiseReducer.loading]: false,
          [promiseReducer.key]: promiseReducer.failData,
        });
      });
    });
  });
};

export const generateTestsForSetReducers = (reducer, defaultState, setReducers) => {
  describe('Reducers that set only one value', () => {
    setReducers.forEach((setReducer) => {
      describe(setReducer.name, () => {
        it(setReducer.description, () => {
          const requestAction = {
            type: setReducer.name,
            [setReducer.key]: setReducer.sendData,
          };

          expect(reducer(defaultState, requestAction)).toEqual({
            ...defaultState,
            [setReducer.key]: setReducer.testData,
          });
        });
      });
    });
  });
};
