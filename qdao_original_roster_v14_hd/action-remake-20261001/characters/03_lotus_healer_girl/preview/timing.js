'use strict';
const ActionTiming = (() => {
  function durations(action, frames) { return frames.map(f => action === 'run' ? 60 : f.durationMs); }
  function total(ds) { return ds.reduce((sum, n) => sum + n, 0); }
  function frameAt(time, ds) {
    const cycle=total(ds), t=((time%cycle)+cycle)%cycle;
    let end=0;
    for(let n=0;n<ds.length;n++){end+=ds[n];if(t<end)return n;}
    return ds.length-1;
  }
  return {durations,total,frameAt};
})();
if(typeof module!=='undefined')module.exports=ActionTiming;
