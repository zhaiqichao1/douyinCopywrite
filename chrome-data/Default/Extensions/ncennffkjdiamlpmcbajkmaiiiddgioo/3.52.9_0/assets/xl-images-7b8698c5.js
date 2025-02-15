import"./modulepreload-polyfill-2ad73d06.js";import{n as e,d as t,r as i,a as r,c as s,o as n,b as a,e as l,w as o,f as d,g as u,h as c,i as h,j as p,t as v,k as f,l as g,F as m,m as A,u as y,p as b,q as w,s as x,v as _}from"./runtime-dom.esm-bundler-cb82e4a9.js";import{s as L}from"./stat-ffa8f2e7.js";import{i as E,m as k}from"./util-1fabc922.js";import{u as C}from"./index-9000aff5.js";
/*!
 * Vue-Lazyload.js v3.0.0
 * (c) 2023 Awe <hilongjw@gmail.com>
 * Released under the MIT License.
 */function I(e,t){return e(t={exports:{}},t.exports),t.exports}var Q=I((function(e){const t=Object.prototype.toString,i=Object.prototype.propertyIsEnumerable,r=Object.getOwnPropertySymbols;e.exports=(e,...s)=>{if("function"!=typeof(n=e)&&"[object Object]"!==t.call(n)&&!Array.isArray(n))throw new TypeError("expected the first argument to be an object");var n;if(0===s.length||"function"!=typeof Symbol||"function"!=typeof r)return e;for(let t of s){let s=r(t);for(let r of s)i.call(t,r)&&(e[r]=t[r])}return e}})),$=Object.freeze({__proto__:null,default:Q,__moduleExports:Q}),B=$&&Q||$,S=I((function(e){const t=Object.prototype.toString,i=e=>"__proto__"!==e&&"constructor"!==e&&"prototype"!==e,r=e.exports=(e,...t)=>{let n=0;var a;for(("object"==typeof(a=e)?null===a:"function"!=typeof a)&&(e=t[n++]),e||(e={});n<t.length;n++)if(s(t[n])){for(const a of Object.keys(t[n]))i(a)&&(s(e[a])&&s(t[n][a])?r(e[a],t[n][a]):e[a]=t[n][a]);B(e,t[n])}return e};function s(e){return"function"==typeof e||"[object Object]"===t.call(e)}}));const T="undefined"!=typeof window&&null!==window,z=function(){if(T&&"IntersectionObserver"in window&&"IntersectionObserverEntry"in window&&"intersectionRatio"in window.IntersectionObserverEntry.prototype)return"isIntersecting"in window.IntersectionObserverEntry.prototype||Object.defineProperty(window.IntersectionObserverEntry.prototype,"isIntersecting",{get:function(){return this.intersectionRatio>0}}),!0;return!1}();const j="event",O="observer";function M(e,t){if(!e.length)return;const i=e.indexOf(t);return i>-1?e.splice(i,1):void 0}function R(e,t){if("IMG"!==e.tagName||!e.getAttribute("data-srcset"))return"";let i=e.getAttribute("data-srcset").trim().split(",");const r=[],s=e.parentNode.offsetWidth*t;let n,a,l;i.forEach(e=>{e=e.trim(),n=e.lastIndexOf(" "),-1===n?(a=e,l=99999):(a=e.substr(0,n),l=parseInt(e.substr(n+1,e.length-n-2),10)),r.push([l,a])}),r.sort((e,t)=>{if(e[0]<t[0])return 1;if(e[0]>t[0])return-1;if(e[0]===t[0]){if(-1!==t[1].indexOf(".webp",t[1].length-5))return 1;if(-1!==e[1].indexOf(".webp",e[1].length-5))return-1}return 0});let o,d="";for(let u=0;u<r.length;u++){o=r[u],d=o[1];const e=r[u+1];if(e&&e[0]<s){d=o[1];break}if(!e){d=o[1];break}}return d}const H=(e=1)=>T&&window.devicePixelRatio||e;function W(){if(!T)return!1;let e=!0;function t(e,t){const i=new Image;i.onload=function(){const e=i.width>0&&i.height>0;t(e)},i.onerror=function(){t(!1)},i.src="data:image/webp;base64,"+{lossy:"UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",lossless:"UklGRhoAAABXRUJQVlA4TA0AAAAvAAAAEAcQERGIiP4HAA==",alpha:"UklGRkoAAABXRUJQVlA4WAoAAAAQAAAAAAAAAAAAQUxQSAwAAAARBxAR/Q9ERP8DAABWUDggGAAAABQBAJ0BKgEAAQAAAP4AAA3AAP7mtQAAAA==",animation:"UklGRlIAAABXRUJQVlA4WAoAAAASAAAAAAAAAAAAQU5JTQYAAAD/////AABBTk1GJgAAAAAAAAAAAAAAAAAAAGQAAABWUDhMDQAAAC8AAAAQBxAREYiI/gcA"}[e]}return t("lossy",t=>{e=t}),t("lossless",t=>{e=t}),t("alpha",t=>{e=t}),t("animation",t=>{e=t}),e}const q=function(){if(!T)return!1;let e=!1;try{const t=Object.defineProperty({},"passive",{get:function(){e=!0}});window.addEventListener("test",V,t)}catch(t){}return e}(),D={on(e,t,i,r=!1){q?e.addEventListener(t,i,{capture:r,passive:!0}):e.addEventListener(t,i,r)},off(e,t,i,r=!1){e.removeEventListener(t,i,r)}},N=(e,t,i)=>{let r=new Image;if(!e||!e.src){const e=new Error("image src is required");return i(e)}e.cors&&(r.crossOrigin=e.cors),r.src=e.src,r.onload=function(){t({naturalHeight:r.naturalHeight,naturalWidth:r.naturalWidth,src:r.src}),r=null},r.onerror=function(e){i(e)}},P=(e,t)=>"undefined"!=typeof getComputedStyle?getComputedStyle(e,null).getPropertyValue(t):e.style[t],U=e=>P(e,"overflow")+P(e,"overflowY")+P(e,"overflowX");function V(){}class G{constructor(e){this.max=e||100,this._caches=[]}has(e){return this._caches.indexOf(e)>-1}add(e){this.has(e)||(this._caches.push(e),this._caches.length>this.max&&this.free())}free(){this._caches.shift()}}class J{constructor(e,t,i,r,s,n,a,l,o,d){this.el=e,this.src=t,this.error=i,this.loading=r,this.bindType=s,this.attempt=0,this.cors=l,this.naturalHeight=0,this.naturalWidth=0,this.options=a,this.rect={},this.$parent=n,this.elRenderer=o,this._imageCache=d,this.performanceData={init:Date.now(),loadStart:0,loadEnd:0},this.filter(),this.initState(),this.render("loading",!1)}initState(){"dataset"in this.el?this.el.dataset.src=this.src:this.el.setAttribute("data-src",this.src),this.state={loading:!1,error:!1,loaded:!1,rendered:!1}}record(e){this.performanceData[e]=Date.now()}update(e){const t=this.src;this.src=e.src,this.loading=e.loading,this.error=e.error,this.filter(),t!==this.src&&(this.attempt=0,this.initState())}getRect(){this.rect=this.el.getBoundingClientRect()}checkInView(){return this.getRect(),this.rect.top<window.innerHeight*this.options.preLoad&&this.rect.bottom>this.options.preLoadTop&&this.rect.left<window.innerWidth*this.options.preLoad&&this.rect.right>0}filter(){for(const e in this.options.filter)this.options.filter[e](this,this.options)}renderLoading(e){this.state.loading=!0,N({src:this.loading,cors:this.cors},()=>{this.render("loading",!1),this.state.loading=!1,e()},()=>{e(),this.state.loading=!1,this.options.silent})}load(e=V){return this.attempt>this.options.attempt-1&&this.state.error?(this.options.silent,void e()):this.state.rendered&&this.state.loaded?void 0:this._imageCache.has(this.src)?(this.state.loaded=!0,this.render("loaded",!0),this.state.rendered=!0,e()):void this.renderLoading(()=>{this.attempt++,this.options.adapter.beforeLoad&&this.options.adapter.beforeLoad(this,this.options),this.record("loadStart"),N({src:this.src,cors:this.cors},t=>{this.naturalHeight=t.naturalHeight,this.naturalWidth=t.naturalWidth,this.state.loaded=!0,this.state.error=!1,this.record("loadEnd"),this.render("loaded",!1),this.state.rendered=!0,this._imageCache.add(this.src),e()},e=>{this.options.silent,this.state.error=!0,this.state.loaded=!1,this.render("error",!1)})})}render(e,t){this.elRenderer(this,e,t)}performance(){let e="loading",t=0;return this.state.loaded&&(e="loaded",t=(this.performanceData.loadEnd-this.performanceData.loadStart)/1e3),this.state.error&&(e="error"),{src:this.src,state:e,time:t}}$destroy(){this.el=null,this.src="",this.error=null,this.loading="",this.bindType=null,this.attempt=0}}const X="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",Y=["scroll","wheel","mousewheel","resize","animationend","transitionend","touchmove"],F={rootMargin:"0px",threshold:0};class K{constructor({preLoad:e,error:t,throttleWait:i,preLoadTop:r,dispatchEvent:s,loading:n,attempt:a,silent:l=!0,scale:o,listenEvents:d,filter:u,adapter:c,observer:h,observerOptions:p}){this.version='"3.0.0"',this.lazyContainerMananger=null,this.mode=j,this.ListenerQueue=[],this.TargetIndex=0,this.TargetQueue=[],this.options={silent:l,dispatchEvent:!!s,throttleWait:i||200,preLoad:e||1.3,preLoadTop:r||0,error:t||X,loading:n||X,attempt:a||3,scale:o||H(o),listenEvents:d||Y,supportWebp:W(),filter:u||{},adapter:c||{},observer:!!h,observerOptions:p||F},this._initEvent(),this._imageCache=new G(200),this.lazyLoadHandler=function(e,t){let i=null,r=0;return function(){if(i)return;const s=Date.now()-r,n=this,a=arguments,l=function(){r=Date.now(),i=!1,e.apply(n,a)};s>=t?l():i=setTimeout(l,t)}}(this._lazyLoadHandler.bind(this),this.options.throttleWait),this.setMode(this.options.observer?O:j)}performance(){const e=[];return this.ListenerQueue.map(t=>e.push(t.performance())),e}addLazyBox(e){this.ListenerQueue.push(e),T&&(this._addListenerTarget(window),this._observer&&this._observer.observe(e.el),e.$el&&e.$el.parentNode&&this._addListenerTarget(e.$el.parentNode))}add(t,i,r){if(this.ListenerQueue.some(e=>e.el===t))return this.update(t,i),e(this.lazyLoadHandler);let{src:s,loading:n,error:a,cors:l}=this._valueFormatter(i.value);e(()=>{s=R(t,this.options.scale)||s,this._observer&&this._observer.observe(t);const r=Object.keys(i.modifiers)[0];let o;r&&(o=i.instance.$refs[r],o=o?o.el||o:document.getElementById(r)),o||(o=(e=>{if(!T)return;if(!(e instanceof Element))return window;let t=e;for(;t&&t!==document.body&&t!==document.documentElement&&t.parentNode;){if(/(scroll|auto)/.test(U(t)))return t;t=t.parentNode}return window})(t));const d=new J(t,s,a,n,i.arg,o,this.options,l,this._elRenderer.bind(this),this._imageCache);this.ListenerQueue.push(d),T&&(this._addListenerTarget(window),this._addListenerTarget(o)),e(this.lazyLoadHandler)})}update(t,i,r){let{src:s,loading:n,error:a}=this._valueFormatter(i.value);s=R(t,this.options.scale)||s;const l=this.ListenerQueue.find(e=>e.el===t);l?l.update({src:s,loading:n,error:a}):"loaded"===t.getAttribute("lazy")&&t.dataset.src===s||this.add(t,i,r),this._observer&&(this._observer.unobserve(t),this._observer.observe(t)),e(this.lazyLoadHandler)}remove(e){if(!e)return;this._observer&&this._observer.unobserve(e);const t=this.ListenerQueue.find(t=>t.el===e);t&&(this._removeListenerTarget(t.$parent),this._removeListenerTarget(window),M(this.ListenerQueue,t),t.$destroy&&t.$destroy())}removeComponent(e){e&&(M(this.ListenerQueue,e),this._observer&&this._observer.unobserve(e.el),e.$parent&&e.$el.parentNode&&this._removeListenerTarget(e.$el.parentNode),this._removeListenerTarget(window))}setMode(e){z||e!==O||(e=j),this.mode=e,e===j?(this._observer&&(this.ListenerQueue.forEach(e=>{this._observer.unobserve(e.el)}),this._observer=null),this.TargetQueue.forEach(e=>{this._initListen(e.el,!0)})):(this.TargetQueue.forEach(e=>{this._initListen(e.el,!1)}),this._initIntersectionObserver())}_addListenerTarget(e){if(!e)return;let t=this.TargetQueue.find(t=>t.el===e);return t?t.childrenCount++:(t={el:e,id:++this.TargetIndex,childrenCount:1,listened:!0},this.mode===j&&this._initListen(t.el,!0),this.TargetQueue.push(t)),this.TargetIndex}_removeListenerTarget(e){this.TargetQueue.forEach((t,i)=>{t.el===e&&(t.childrenCount--,t.childrenCount||(this._initListen(t.el,!1),this.TargetQueue.splice(i,1),t=null))})}_initListen(e,t){this.options.listenEvents.forEach(i=>D[t?"on":"off"](e,i,this.lazyLoadHandler))}_initEvent(){this.Event={listeners:{loading:[],loaded:[],error:[]}},this.$on=(e,t)=>{this.Event.listeners[e]||(this.Event.listeners[e]=[]),this.Event.listeners[e].push(t)},this.$once=(e,t)=>{const i=this;this.$on(e,(function r(){i.$off(e,r),t.apply(i,arguments)}))},this.$off=(e,t)=>{if(t)M(this.Event.listeners[e],t);else{if(!this.Event.listeners[e])return;this.Event.listeners[e].length=0}},this.$emit=(e,t,i)=>{this.Event.listeners[e]&&this.Event.listeners[e].forEach(e=>e(t,i))}}_lazyLoadHandler(){const e=[];this.ListenerQueue.forEach((t,i)=>{t.el&&t.el.parentNode&&!t.state.loaded||e.push(t);t.checkInView()&&(t.state.loaded||t.load())}),e.forEach(e=>{M(this.ListenerQueue,e),e.$destroy&&e.$destroy()})}_initIntersectionObserver(){z&&(this._observer=new IntersectionObserver(this._observerHandler.bind(this),this.options.observerOptions),this.ListenerQueue.length&&this.ListenerQueue.forEach(e=>{this._observer.observe(e.el)}))}_observerHandler(e){e.forEach(e=>{e.isIntersecting&&this.ListenerQueue.forEach(t=>{if(t.el===e.target){if(t.state.loaded)return this._observer.unobserve(t.el);t.load()}})})}_elRenderer(e,t,i){if(!e.el)return;const{el:r,bindType:s}=e;let n;switch(t){case"loading":n=e.loading;break;case"error":n=e.error;break;default:n=e.src}if(s?r.style[s]='url("'+n+'")':r.getAttribute("src")!==n&&r.setAttribute("src",n),r.setAttribute("lazy",t),this.$emit(t,e,i),this.options.adapter[t]&&this.options.adapter[t](e,this.options),this.options.dispatchEvent){const i=new CustomEvent(t,{detail:e});r.dispatchEvent(i)}}_valueFormatter(e){return null!==(t=e)&&"object"==typeof t?(!e.src&&this.options.silent,{src:e.src,loading:e.loading||this.options.loading,error:e.error||this.options.error,cors:this.options.cors}):{src:e,loading:this.options.loading,error:this.options.error,cors:this.options.cors};var t}}const Z=(e,t)=>{let i=r({});return{rect:i,checkInView:()=>(i=e.value.getBoundingClientRect(),T&&i.top<window.innerHeight*t&&i.bottom>0&&i.left<window.innerWidth*t&&i.right>0)}};class ee{constructor(e){this.lazy=e,e.lazyContainerMananger=this,this._queue=[]}bind(e,t,i){const r=new ie(e,t,i,this.lazy);this._queue.push(r)}update(e,t,i){const r=this._queue.find(t=>t.el===e);r&&r.update(e,t)}unbind(e,t,i){const r=this._queue.find(t=>t.el===e);r&&(r.clear(),M(this._queue,r))}}const te={selector:"img",error:"",loading:""};class ie{constructor(e,t,i,r){this.el=e,this.vnode=i,this.binding=t,this.options={},this.lazy=r,this._queue=[],this.update(e,t)}update(e,t){this.el=e,this.options=S({},te,t.value);this.getImgs().forEach(e=>{this.lazy.add(e,S({},this.binding,{value:{src:e.getAttribute("data-src")||e.dataset.src,error:e.getAttribute("data-error")||e.dataset.error||this.options.error,loading:e.getAttribute("data-loading")||e.dataset.loading||this.options.loading}}),this.vnode)})}getImgs(){return Array.from(this.el.querySelectorAll(this.options.selector))}clear(){this.getImgs().forEach(e=>this.lazy.remove(e)),this.vnode=null,this.binding=null,this.lazy=null}}var re=e=>t({setup(t,{slots:d}){const u=i(),c=r({src:"",error:"",loading:"",attempt:e.options.attempt}),h=r({loaded:!1,error:!1,attempt:0}),{rect:p,checkInView:v}=Z(u,e.options.preLoad),f=i(""),g=(t=V)=>{if(h.attempt>c.attempt-1&&h.error)return e.options.silent,t();const i=c.src;N({src:i},({src:e})=>{f.value=e,h.loaded=!0},()=>{h.attempt++,f.value=c.error,h.error=!0})},m=s(()=>({el:u.value,rect:p,checkInView:v,load:g,state:h}));n(()=>{e.addLazyBox(m.value),e.lazyLoadHandler()}),a(()=>{e.removeComponent(m.value)});return o(()=>t.src,()=>{(()=>{const{src:i,loading:r,error:s}=e._valueFormatter(t.src);h.loaded=!1,c.src=i,c.error=s,c.loading=r,f.value=c.loading})(),e.addLazyBox(m.value),e.lazyLoadHandler()},{immediate:!0}),()=>{var e;return l(t.tag||"img",{src:f.value,ref:u},[null===(e=d.default)||void 0===e?void 0:e.call(d)])}}}),se={install(e,o={}){const d=new K(o),u=new ee(d);if(Number(e.version.split(".")[0])<3)return new Error("Vue version at least 3.0");e.config.globalProperties.$Lazyload=d,e.provide("Lazyload",d),o.lazyComponent&&e.component("lazy-component",(e=>t({props:{tag:{type:String,default:"div"}},emits:["show"],setup(t,{emit:o,slots:d}){const u=i(),c=r({loaded:!1,error:!1,attempt:0}),h=i(!1),{rect:p,checkInView:v}=Z(u,e.options.preLoad),f=()=>{h.value=!0,c.loaded=!0,o("show",h.value)},g=s(()=>({el:u.value,rect:p,checkInView:v,load:f,state:c}));return n(()=>{e.addLazyBox(g.value),e.lazyLoadHandler()}),a(()=>{e.removeComponent(g.value)}),()=>{var e;return l(t.tag,{ref:u},[h.value&&(null===(e=d.default)||void 0===e?void 0:e.call(d))])}}}))(d)),o.lazyImage&&e.component("lazy-image",re(d)),e.directive("lazy",{beforeMount:d.add.bind(d),beforeUpdate:d.update.bind(d),updated:d.lazyLoadHandler.bind(d),unmounted:d.remove.bind(d)}),e.directive("lazy-container",{beforeMount:u.bind.bind(u),updated:u.update.bind(u),unmounted:u.unbind.bind(u)})}};function ne(){const e=[];for(const t of document.images)t.src&&e.push({src:t.src,width:t.width,height:t.height,naturalWidth:t.naturalWidth,naturalHeight:t.naturalHeight});return e}const ae={addClass(e,t){if(!t)return;const i=((e.getAttribute("class")||"")+" "+t).trim();e.setAttribute("class",i)},toggleClass(e,t){const i=e.getAttribute("class")||"";if(-1===i.indexOf(t))this.addClass(e,t);else{const r=i.replace(t,"").trim();e.setAttribute("class",r)}},hasClass:(e,t)=>(e.getAttribute("class")||"").includes(t),removeClass(e,t){if(!t)return;const i=(e.getAttribute("class")||"").replace(t,"").trim();e.setAttribute("class",i)},debounce(e,t){let i;return function(){clearTimeout(i),i=setTimeout(e,t)}}},le={class:"xl-download"},oe={class:"xl-download__header"},de={class:"xl-download__info"},ue={id:"selected"},ce={id:"total"},he=["onClick"],pe=h("i",{class:"icon-down"},null,-1),ve=h("a",{href:"https://www.xunlei.com/",target:"_blank",class:"xl-logo",title:"迅雷"},null,-1),fe={class:"xl-download__operate"},ge=h("span",{class:"xl-download__operate-text"},"图片类型：",-1),me={class:"xl-download__type",id:"pictureType",style:{width:"547px"}},Ae=["onClick","data-id"],ye=h("div",{class:"xl-size"},[h("span",null,"宽度："),h("div",{id:"widthSlider"})],-1),be=h("div",{class:"xl-size"},[h("span",null,"高度："),h("div",{id:"heightSlider"})],-1),we={class:"xl-download__body"},xe={class:"xl-list"},_e={key:0,id:"pictureWrap"},Le=["onClick"];_({__name:"download-images",setup(e){const t=i(""),a=s(()=>0===S.value.length);let l=null,_=i([{type:"默认",key:"all",count:0,select:!0},{type:"JPEG",key:"jpeg",count:0,select:!1},{type:"PNG",key:"png",count:0,select:!1},{type:"GIF",key:"gif",count:0,select:!1},{type:"其他",key:"other",count:0,select:!1}]);const I=r({png:[],gif:[],jpeg:[],other:[]}),Q=i([]),$=r({png:[],gif:[],jpeg:[],other:[]}),B=i([]),S=i([]),T=i(0),z=i(0),j=i(_.value.filter(e=>e.select).map(e=>e.key)),O=r({list:[]}),M=i([0,T.value]),R=i([0,z.value]),H=["png","jpeg","gif","jpg"];o(O.list,e=>{B.value=e.list},{deep:!0});let W=[],q=[],D=[];function N(){const[e,t]=M.value,[i,r]=R.value;let s=[];const n=j.value;if(0===n.length||n.includes("all"))s=[...O.list];else for(let a in n){const e=(n[a]||"").toLowerCase();"all"!==e&&I[e]&&s.push(...I[e])}return[...new Set(s)].filter(s=>{const{naturalWidth:n,naturalHeight:a}=s;return e<=n&&n<=t&&(i<=a&&a<=r)})}o(B,(e,t)=>{0===j.value.length?S.value=[]:S.value=e.map(e=>e.src)}),o(T,(e,t)=>{M.value=[0,e]}),o(z,(e,t)=>{R.value=[0,e]}),o(M,(e,t)=>{const i=N();B.value=[...i]}),o(R,(e,t)=>{const i=N();B.value=[...i]}),o(()=>O.list,(e,t)=>{O.list.map(e=>{const t=function(e){const t=function(e){const t=e.match(/\.([^\.]+)$/);return t?t[1]:""}(e);let i="other";return H.includes(t)&&(i="jpg"===t?"jpeg":t),i}(e.src),i=[...new Set([...I[t],e])];I[t]=i}),B.value=N()},{deep:!0}),o(j,(e,t)=>{if(0===(null==e?void 0:e.length))B.value=O.list;else{const t=[];if(e)for(let i in e){const r=(e[i]||"").toLowerCase();"all"===r?t.push(...O.list):I[r]&&t.push(...I[r])}B.value=N()}});let P=function(e){this.config=Object.assign({},this.config,e),this.render()};function U(e,t){const i=[...e],r=i.indexOf(t);return r>-1?i.splice(r,1):i.push(t),i}function V(e){let t=[..._.value],i=e.key;const r=t.find(e=>e.key===i);if(!r)return t;if(r.select=!r.select,"all"===e.key)t.forEach(e=>{"all"!==e.key&&(e.select=!1)});else{const e=t.find(e=>"all"===e.key);e&&(e.select=!1)}_.value=t,j.value=_.value.filter(e=>e.select).map(e=>e.key)}function G(e){!function(e,t){const i=t.find(e=>"content-type"===e.name||"Content-Type"===e.name);let r=i?i.value.split("/")[1].toLowerCase():"other";H.includes(r)?"jpg"===r&&(r="jpeg"):r="other";const s={url:e,type:r};Q.value.push(s),$[r].push(s)}(e.url,e.responseHeaders)}function J(){if(a.value)return;const e=S.value;if(!e.length)return void alert("请选择您需要下载的图片! ");const i=_.value.filter(e=>e.select).map(e=>e.key);L(1022,933,`value1=${e.length}&value2=${_.value[0].count}&value5=${i.join(",")}&value6=(${W.join("-")})*(${q.join("-")})`),E?k(S.value):chrome.runtime.sendMessage({name:"xl_download_multi",referurl:t.value,urls:S.value.filter(e=>0===e.indexOf("http"))})}function X(e){const{naturalWidth:t,naturalHeight:i}=e;let r=t,s=i;if(t>250||i>250){const e=Math.min(250/t,250/i);r=t*e,s=i*e}return{width:r,height:s}}return P.prototype.config={min:0,max:100,value:0,range:!1,disabled:!1,theme:"#009688",step:1},P.prototype.render=function(e){const t=this,i=t.config,r=document.createElement("div");if(r.className="xl-slider",i.step<1&&(i.step=1),i.max<i.min&&(i.max=i.min+i.step),i.range){i.value="object"==typeof i.value?i.value:[i.min,i.value];const e=Math.min(i.value[0],i.value[1]),t=Math.max(i.value[0],i.value[1]);i.value[0]=e>i.min?e:i.min,i.value[1]=t>i.min?t:i.min,i.value[0]=i.value[0]>i.max?i.max:i.value[0],i.value[1]=i.value[1]>i.max?i.max:i.value[1];var s=Math.floor((i.value[0]-i.min)/(i.max-i.min)*100),n=Math.floor((i.value[1]-i.min)/(i.max-i.min)*100),a=n-s+"%";s+="%",n+="%"}else{"object"==typeof i.value&&(i.value=Math.min.apply(null,i.value)),i.value<i.min&&(i.value=i.min),i.value>i.max&&(i.value=i.max);a=Math.floor((i.value-i.min)/(i.max-i.min)*100)+"%"}const l=i.disabled?"#c2c2c2":i.theme,o=`<div class="xl-slider-bar" style="background:${l};width:${a};left:${s||0};"></div>\n       <div class="xl-slider-wrap" style="left:${s||a};">\n        <div class="xl-slider-wrap-btn" style="border: 2px solid ${l};"></div>\n        <div class="xl-slider-wrap-value">${i.range?i.value[0]:i.value}</div>\n       </div>\n      ${i.range?`<div class="xl-slider-wrap" style="left: ${n};">\n             <div class="xl-slider-wrap-btn" style="border: 2px solid ${l};"></div>\n             <div class="xl-slider-wrap-value">${i.value[1]}</div>\n            </div>`:""}\n       </div>`;r.innerHTML=o,t.container=document.querySelector(i.elem),t.container.appendChild(r),t.sliderInner=t.container.querySelector(".xl-slider"),t.sliderBar=t.container.querySelector(".xl-slider-bar"),t.sliderBtnWrap=t.container.querySelectorAll(".xl-slider-wrap"),i.range?(t.sliderBtnWrap[0].dataset.value=i.value[0],t.sliderBtnWrap[1].dataset.value=i.value[1]):t.sliderBtnWrap[0].dataset.value=i.value,t.slide()},P.prototype.slide=function(e,t,i){let r=this,s=r.config,n=r.sliderInner,a=function(){return n.offsetWidth},l=r.sliderBtnWrap,o=0,d=100,u=1,c=100/((s.max-s.min)/Math.ceil(s.step)),h=function(e,t){if(e=function(e){return(e=Math.ceil(e)*c>100?Math.ceil(e)*c:Math.round(e)*c)>100?100:e}(e),0===t?o=e:d=e,d-o<=0)return;l[t].style.left=e+"%",l[t].style.zIndex=u++;let i=p(l[0].offsetLeft),n=s.range?p(l[1].offsetLeft):0;i=i>100?100:i,n=n>100?100:n;let a=Math.min(i,n),h=Math.abs(n-i);r.sliderBar.style.width=h+"%",r.sliderBar.style.left=a+"%";let f=s.min+Math.round((s.max-s.min)*e/100);l[t].dataset.value=f,v(t,f);let g=[];s.range&&(g=[+l[0].dataset.value,+l[1].dataset.value],g[0]>g[1]&&g.reverse()),s.change&&s.change(s.range?g:f)},p=function(e){let t=e/a()*100/c,i=Math.round(t)*c;return e==a()&&(i=Math.ceil(t)*c),i},v=function(e,t){let i=l[e].querySelector(".xl-slider-wrap-value");i.innerText=t;let s=l[1].querySelector(".xl-slider-wrap-value").getBoundingClientRect(),a=l[0].querySelector(".xl-slider-wrap-value").getBoundingClientRect(),o=s.left-a.left-a.width,d=n.getBoundingClientRect();if(o<5||o<0){let l=r.container.querySelector(".xl-slider-temp-value"+e);l||(l=document.createElement("div"),l.className="xl-slider-temp-value"+e,l.innerText=t,n.appendChild(l),i.style.visibility="hidden"),l.style.left=0===e?s.left-s.width/2-d.left-5+"px":a.right+s.width/2-d.left+5+"px",l.innerText=t}else{let e=r.container.querySelector(".xl-slider-temp-value0"),t=r.container.querySelector(".xl-slider-temp-value1");e&&(n.removeChild(e),l[0].querySelector(".xl-slider-wrap-value").style.visibility="visible"),t&&(n.removeChild(t),l[1].querySelector(".xl-slider-wrap-value").style.visibility="visible")}};if("set"===e)return h(t,i);r.sliderBtnWrap.forEach((e,t)=>{let i=e.querySelector(".xl-slider-wrap-btn");i.addEventListener("mousedown",(function(e){e=e||window.event;let r=i.parentNode.offsetLeft,s=e.clientX;!function(e,t){let i=document.getElementById("LAY-slider-moving");if(!i){let e=document.createElement("div");e.id="LAY-slider-moving",e.className="xl-auxiliar-moving",document.body.appendChild(e),i=document.getElementById("LAY-slider-moving")}let r=function(){t&&t(),i.parentNode.removeChild(i)};i.addEventListener("mousemove",e),i.addEventListener("mouseup",r),i.addEventListener("mouseleave",r)}((function(e){e=e||window.event;let i=r+e.clientX-s;i<0&&(i=0),i>a()&&(i=a());let n=i/a()*100/c;h(n,t),e.preventDefault()}),(function(){}))}))}),n.addEventListener("click",(function(e){let t,i=this.getBoundingClientRect(),r=e.clientX-i.left;r<0&&(r=0),r>a()&&(r=a());let n=r/a()*100/c;t=s.range&&Math.abs(r-l[0].offsetLeft)>Math.abs(r-l[1].offsetLeft)?1:0,h(n,t),e.preventDefault()}))},P.prototype.onChange=function(e){this.config.change=t=>{ae.debounce(e(t),100)}},P.prototype.setValue=function(e,t){return this.config.value=e,this.slide("set",e,t||0)},chrome.runtime.onMessage.addListener((e,t,i)=>{"xlMultiPicUpdateDetail"==e.name&&G(e.value)}),n(()=>{l=document.querySelector("#pictureType"),function(){let e=new URL(location.href);if(!e||!e.searchParams)return;let i=e.searchParams.get("tabId");if(!i)return;if(i=Number(i),isNaN(i))return;chrome.tabs.get(i,e=>{e&&(t.value=e.url,chrome.tabs.onRemoved.addListener((function(e,t){e===i&&window.close()})),chrome.scripting.executeScript({target:{tabId:i},func:ne},e=>{let t=[];e&&e[0]&&e[0].result&&(t=e[0].result);let i={},r=[];for(let s of t)i[s.src]||(i[s.src]=!0,r.push(s));!function(e){D=e.filter(e=>(e.select=!0,!(/^data:/.test(e.src)||e.naturalWidth<=1||e.naturalHeight<=1))),O.list=[...new Set(D)],S.value=D.map(e=>e.src);let t=O.list.length;_.value=_.value.map(e=>({...e,count:"all"===e.key?t:0})),O.list.forEach(e=>{const{naturalWidth:t,naturalHeight:i}=e;t>T.value&&(T.value=t),i>z.value&&(z.value=i)});let i=new P({elem:"#widthSlider",min:0,max:T.value,value:[0,T.value],range:!0,theme:"#2670ea"}),r=new P({elem:"#heightSlider",min:0,max:z.value,value:[0,z.value],range:!0,theme:"#2670ea"});W=[0,T.value],q=[0,z.value],i.onChange((function(e){W=e,M.value=e})),r.onChange(e=>{q=e,R.value=e}),l.addEventListener("click",e=>{V(e.target)}),L(1022,932)}(r)}))})}()}),(e,t)=>{const i=d("lazy");return u(),c("div",le,[h("header",oe,[h("div",de,[h("h1",null,[p(" 已选中图片 "),h("span",ue,v(S.value.length),1),p(" 个 ")]),h("p",ce,v(`总共${O.list.length}个`),1),h("a",{class:f(["xl-button",{disable:a.value}]),onClick:g(J,["stop"])},[pe,p("下载图片 ")],10,he)]),ve]),h("div",fe,[ge,h("div",me,[(u(!0),c(m,null,A(y(_),(e,t)=>(u(),c("span",{key:e.key,onClick:g(t=>V(e),["stop"]),class:f({"is-checked2":e.select,"is-disabled":j.value.includes(e.key)&&0===S.value.length}),"data-id":t},[p(v(e.type)+" ",1),h("sup",null,v("all"===e.key?y(D).length:[...new Set(I[e.key])].length),1)],10,Ae))),128))]),ye,be]),h("div",we,[h("div",xe,[B.value.length>0?(u(),c("ul",_e,[(u(!0),c(m,null,A(B.value,(e,t)=>(u(),c("li",{onClick:g(i=>function(e,t){D[t].select=!D[t].select,S.value=U(S.value,e.src),U(S.value,e.src)}(e,t),["stop"]),class:f({"is-checked":S.value.includes((null==e?void 0:e.src)||""),"is-disabled":!S.value.includes((null==e?void 0:e.src)||"")}),key:e.src,style:w({width:X(e).width+"px",height:X(e).height+"px",overflow:"hidden"})},[x(h("img",null,null,512),[[i,`${e.src}${e.src.includes("?")?"&":"?"}${y(C)}}`]]),h("p",null,v(e.naturalWidth)+"x"+v(e.naturalHeight),1)],14,Le))),128))])):b("",!0)])])])}}}).use(se,{observer:!0,observerOptions:{rootMargin:"0px",threshold:.1},preLoad:1.3,attempt:3}).mount("#app");
