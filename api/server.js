const express = require('express');
const yahooFinance = require('yahoo-finance2').default;

const app = express();

app.get('/api/live', async (req, res) => {
  try {
    const quote = await yahooFinance.quote('^GSPC');
    res.json({
      price: quote.regularMarketPrice,
      change: quote.regularMarketChange,
      change_pct: quote.regularMarketChangePercent,
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/historical', async (req, res) => {
  try {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setFullYear(startDate.getFullYear() - 5);

    const result = await yahooFinance.historical('^GSPC', {
      period1: startDate,
      period2: endDate,
      interval: '1d'
    });

    res.json(result.map(d => ({
      date: d.date.toISOString().split('T')[0],
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
      volume: d.volume
    })));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = app;

if (require.main === module) {
  const PORT = 3001;
  app.listen(PORT, () => console.log(`API server running on port ${PORT}`));
}
