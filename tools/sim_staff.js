// Runs the game's own day simulation with different teams and prints what each team earns.
// Usage: node tools/sim_staff.js [days=60] [stars=1]
// Loads index.html in the pre-installed Chromium (Playwright), starts from a new game, puts the buyer in charge of
// the pantry (tier 2: no hiring on its own, so the team stays as set) and, for each team, plays the same number of
// days from the same starting point with managerMorning() + simulateDay() + finishDay(), as the Day screen does.
const {chromium}=require('playwright');
const path=require('path');
const DAYS=+process.argv[2]||60,STARS=+process.argv[3]||1;
// each team: [role, speed, second skill (cooking or charm)] per person; wages follow wageOf(), as for a candidate
const TEAMS={
  'start (1 cook 3/3, 1 waiter 3/3)':[['cook',3,3],['waiter',3,3]],
  'slow cook (1/3)':[['cook',1,3],['waiter',3,3]],
  'fast cook (5/3)':[['cook',5,3],['waiter',3,3]],
  'slow waiter (1/3)':[['cook',3,3],['waiter',1,3]],
  'fast waiter (5/3)':[['cook',3,3],['waiter',5,3]],
  'good cooking + charm (3/5)':[['cook',3,5],['waiter',3,5]],
  'poor cooking + charm (3/1)':[['cook',3,1],['waiter',3,1]],
  'all 5/5':[['cook',5,5],['waiter',5,5]],
  '2 cooks + 2 waiters 3/3':[['cook',3,3],['cook',3,3],['waiter',3,3],['waiter',3,3]],
};
(async()=>{
  const b=await chromium.launch(),pg=await b.newPage();
  const errs=[];pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto('file://'+path.resolve(__dirname,'../index.html'));
  await pg.waitForFunction(()=>typeof state!=='undefined'&&state);
  const rows=await pg.evaluate(({TEAMS,DAYS,STARS})=>{
    closeModal();
    const base=freshState();base.chef='Sim';base.shop='Sim';base.seenIntro=true;base.tier=2;base.rep=STARS;
    const snap=JSON.stringify(base),out=[];
    for(const [name,team] of Object.entries(TEAMS)){
      state=ensureShops(JSON.parse(snap));
      state.staff=team.map(([r,sp,sk])=>({...newPerson(r,sp,sk),w:wageOf(r,sp,sk)}));
      const m0=state.money;let served=0,lost=0,happy=0,N=0,wage=0;
      for(let d=0;d<DAYS;d++){managerMorning();const res=simulateDay();const f=finishDay(res);
        served+=res.served;lost+=res.full;happy+=res.happy;N+=res.N;wage+=f.sal;if(state.over)break}
      out.push({team:name,kitchen:capacity(),room:serviceCap(),'served/day':(served/DAYS).toFixed(1),'lost to queue/day':(lost/DAYS).toFixed(1),
        'happy %':Math.round(happy/Math.max(1,served)*100),'wages/day':'$'+(wage/DAYS).toFixed(0),'profit/day':'$'+((state.money-m0)/DAYS).toFixed(0),'stars at end':state.rep.toFixed(2)});
    }
    return out},{TEAMS,DAYS,STARS});
  console.log(`${DAYS} days from a new game, starting at ${STARS} star(s), the buyer running the pantry:`);
  console.table(rows);
  if(errs.length)console.log('page errors:',errs);
  await b.close();
})();
