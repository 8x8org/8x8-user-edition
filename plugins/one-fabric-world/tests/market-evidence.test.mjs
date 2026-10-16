import test from 'node:test';
import assert from 'node:assert/strict';
import {validateLocalMarketSnapshot,formatMarketTradeCount,marketClosePath} from '../ui/market-evidence.mjs';
const good=()=>({
 schema:'8x8.public.market.snapshot.v1',
 classification:'LOCAL_IMPORT_UNVERIFIED',scope:'PUBLIC_MARKET_ONLY',
 source_label:'TEST FIXTURE - NOT LIVE',venue:'TEST',
 instrument:'FIXTURE-USD',interval:'1m',
 window_start:'2026-01-01T00:00:00Z',window_end:'2026-01-01T00:03:00Z',observed_at:'2026-01-01T00:03:10Z',
 market_trade_count:'12345678901234567890123456789012345',
 bars:[
  {timestamp:'2026-01-01T00:00:00Z',open:10,high:12,low:9,close:11,volume:100},
  {timestamp:'2026-01-01T00:01:00Z',open:11,high:13,low:10,close:12,volume:99},
  {timestamp:'2026-01-01T00:02:00Z',open:12,high:14,low:11,close:13,volume:105}
 ]
});
test('valid local market snapshot retains sources and independently denominated market trade count',()=>{
 const r=validateLocalMarketSnapshot(good());assert.equal(r.ok,true);
 assert.equal(r.snapshot.scope,'PUBLIC_MARKET_ONLY');assert.equal(r.snapshot.classification,'LOCAL_IMPORT_UNVERIFIED');
 assert.equal(r.snapshot.bars.length,3);assert.equal(r.snapshot.market_trade_count,good().market_trade_count);
});
test('huge exact decimal trade count formats without 53 bit loss',()=>{
 const r=good();assert.equal(formatMarketTradeCount(r.market_trade_count),BigInt(r.market_trade_count).toLocaleString('en-US'));
 assert.equal(formatMarketTradeCount(null),'UNAVAILABLE');
});
test('no trading account or private credentials allowed in public snapshot',()=>{
 const r=good();r.account_fill_count='15';assert.equal(validateLocalMarketSnapshot(r).error,'UNKNOWN_OR_PRIVATE_FIELD');
 delete r.account_fill_count;r.api_key='secret';assert.equal(validateLocalMarketSnapshot(r).error,'UNKNOWN_OR_PRIVATE_FIELD');
});
test('local uploads cannot claim live provider verification',()=>{
 const r=good();r.classification='LIVE_PROVIDER_VERIFIED';assert.equal(validateLocalMarketSnapshot(r).error,'NOT_A_PUBLIC_LOCAL_SNAPSHOT');
});
test('OHLC high low validity enforced',()=>{
 const r=good();r.bars[1].high=10;assert.equal(validateLocalMarketSnapshot(r).error,'INVALID_OHLCV');
});
test('bar times must be ordered and inside declared window',()=>{
 const r=good();r.bars[1].timestamp=r.bars[0].timestamp;assert.equal(validateLocalMarketSnapshot(r).error,'OUT_OF_ORDER_OR_OUTSIDE_WINDOW');
});
test('invalid count and unsupported data fields rejected',()=>{
 const r=good();r.market_trade_count='1e10';assert.equal(validateLocalMarketSnapshot(r).error,'INVALID_TRADE_COUNT');
 r.market_trade_count=null;r.bars[0].account_id='private';assert.equal(validateLocalMarketSnapshot(r).error,'UNKNOWN_BAR_FIELD');
});
test('malformed timestamps and intervals fail closed',()=>{
 const r=good();r.window_end='today';assert.equal(validateLocalMarketSnapshot(r).error,'INVALID_TIMESTAMPS');
 r.window_end='2026-01-01T00:03:00Z';r.interval='1ms';assert.equal(validateLocalMarketSnapshot(r).error,'INVALID_INTERVAL');
});
test('valid close-price geometry fits the plot',()=>{
 const r=validateLocalMarketSnapshot(good()),g=marketClosePath(r.snapshot.bars);
 assert.ok(g.path.startsWith('M'));assert.equal(g.points.length,3);assert.equal(g.minimum,11);
 assert.equal(g.maximum,13);assert.ok(g.points.every(([x,y])=>x>=0&&x<=760&&y>=0&&y<=240));
});
test('constant price avoids divide by zero; invalid geometry fails closed',()=>{
 const r=validateLocalMarketSnapshot(good());r.snapshot.bars.forEach(b=>{b.close=1});
 assert.ok(marketClosePath(r.snapshot.bars).path.startsWith('M'));
 assert.equal(marketClosePath([r.snapshot.bars[0]]),null);
});
