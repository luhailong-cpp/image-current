'use strict';
// Legacy entry now redirects to the current all-action preview.
if(typeof location!=='undefined')location.replace(new URL('actions.html',location.href).href);
