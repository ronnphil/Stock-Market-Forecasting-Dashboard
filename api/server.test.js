const request = require('supertest');

jest.mock('yahoo-finance2', () => ({
  default: {
    quote: jest.fn().mockResolvedValue({
      regularMarketPrice: 5234.18,
      regularMarketChange: 22.45,
      regularMarketChangePercent: 0.43
    }),
    historical: jest.fn().mockResolvedValue([
      {
        date: new Date('2024-01-02'),
        open: 4742.83,
        high: 4763.13,
        low: 4728.75,
        close: 4742.83,
        volume: 3500000000
      }
    ])
  }
}));

const app = require('./server');

describe('GET /api/live', () => {
  it('returns price, change, change_pct, timestamp', async () => {
    const res = await request(app).get('/api/live');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('price', 5234.18);
    expect(res.body).toHaveProperty('change', 22.45);
    expect(res.body).toHaveProperty('change_pct', 0.43);
    expect(res.body).toHaveProperty('timestamp');
  });
});

describe('GET /api/historical', () => {
  it('returns array of OHLCV objects with string dates', async () => {
    const res = await request(app).get('/api/historical');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
    expect(res.body[0]).toMatchObject({
      date: '2024-01-02',
      open: 4742.83,
      close: 4742.83
    });
  });
});
