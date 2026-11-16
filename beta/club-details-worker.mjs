import {clubCampaigns} from './club-details-campaigns.mjs?v=story-recovery-1';
self.onmessage=({data})=>{try{self.postMessage({ok:true,value:clubCampaigns(data.club,data.competition)});}catch(_){self.postMessage({ok:false});}};
