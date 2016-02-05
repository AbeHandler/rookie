import assert from 'assert';

describe('page title', () => {
  it('has the correct page title', () => {
    return browser
      .url('/')
      .getTitle().then((title) => {
        assert.equal(title, 'End-to-End Testing');
      });
  });
});