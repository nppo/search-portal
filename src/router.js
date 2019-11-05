/**
 * This file is the router.js file that gets generated by NuxtJS.
 * We should normalize this file and remove the autogenerated code, but we intend to keep a router file.
 */


import Vue from 'vue'
import Router from 'vue-router'


const _e895237e = () => import('../pages/how-does-it-work/index.vue' /* webpackChunkName: "pages/how-does-it-work/index" */).then(m => m.default || m);
const _e32cc490 = () => import('../pages/communities/index.vue' /* webpackChunkName: "pages/communities/index" */).then(m => m.default || m);
const _70c48e2d = () => import('../pages/materials/search.vue' /* webpackChunkName: "pages/materials/search" */).then(m => m.default || m);
const _77aed046 = () => import('../pages/my/filters/index.vue' /* webpackChunkName: "pages/my/filters/index" */).then(m => m.default || m);
const _169285f4 = () => import('../pages/my/collections.vue' /* webpackChunkName: "pages/my/collections" */).then(m => m.default || m);
const _5330bd0f = () => import('../pages/my/collection.vue' /* webpackChunkName: "pages/my/collection" */).then(m => m.default || m);
const _b5953cb4 = () => import('../pages/my/communities.vue' /* webpackChunkName: "pages/my/communities" */).then(m => m.default || m);
const myCommunity = () => import('../pages/my/community.vue' /* webpackChunkName: "pages/my/community" */).then(m => m.default || m);
const _1c7624f6 = () => import('../pages/my/filters/_id.vue' /* webpackChunkName: "pages/my/filters/_id" */).then(m => m.default || m);
const _45857c92 = () => import('../pages/themes/_id.vue' /* webpackChunkName: "pages/themes/_id" */).then(m => m.default || m);
const _4ed33c85 = () => import('../pages/materials/_id.vue' /* webpackChunkName: "pages/materials/_id" */).then(m => m.default || m);
const _3729fb6e = () => import('../pages/collections/_id.vue' /* webpackChunkName: "pages/collections/_id" */).then(m => m.default || m);
const _e164c612 = () => import('../pages/communities/_community/index.vue' /* webpackChunkName: "pages/communities/_community/index" */).then(m => m.default || m);
const _0624db53 = () => import('../pages/communities/_community/search.vue' /* webpackChunkName: "pages/communities/_community/search" */).then(m => m.default || m);
const _2cdbb9b6 = () => import('../pages/communities/_community/collections/_id.vue' /* webpackChunkName: "pages/communities/_community/collections/_id" */).then(m => m.default || m);
const _ebbee700 = () => import('../pages/index.vue' /* webpackChunkName: "pages/index" */).then(m => m.default || m);
const infoPage = () => import('../pages/info.vue').then(m => m.default || m);

Vue.use(Router);


if (process.client) {
  window.history.scrollRestoration = 'manual'
}
const scrollBehavior = function (to, from, savedPosition) {
  // if the returned position is falsy or an empty object,
  // will retain current scroll position.
  let position = false;

  // if no children detected
  if (to.matched.length < 2) {
    // scroll to the top of the page
    position = { x: 0, y: 0 }
  } else if (to.matched.some((r) => r.components.default.options.scrollToTop)) {
    // if one of the children has scrollToTop option set to true
    position = { x: 0, y: 0 }
  }

  // savedPosition is only available for popstate navigations (back button)
  if (savedPosition) {
    position = savedPosition
  }

  return new Promise((resolve) => {
    // wait for the out transition to complete (if necessary)
    window.$nuxt.$once('triggerScroll', () => {
      // coords will be used if no selector is provided,
      // or if the selector didn't match any element.
      if (to.hash) {
        let hash = to.hash;
        // CSS.escape() is not supported with IE and Edge.
        if (typeof window.CSS !== 'undefined' && typeof window.CSS.escape !== 'undefined') {
          hash = '#' + window.CSS.escape(hash.substr(1))
        }
        try {
          if (document.querySelector(hash)) {
            // scroll to anchor by returning the selector
            position = { selector: hash }
          }
        } catch (e) {
          console.warn('Failed to save scroll position. Please add CSS.escape() polyfill (https://github.com/mathiasbynens/CSS.escape).')
        }
      }
      resolve(position)
    })
  })
};


export function createRouter () {
  return new Router({
    mode: 'history',
    base: '/',
    linkActiveClass: 'nuxt-link-active',
    linkExactActiveClass: 'nuxt-link-exact-active',
    scrollBehavior,
    routes: [
		{
			path: "/en/how-does-it-work",
			component: _e895237e,
			name: "how-does-it-work___en"
		},
		{
			path: "/hoe-werkt-het",
			component: _e895237e,
			name: "how-does-it-work___nl"
		},
		{
			path: "/en/communities",
			component: _e32cc490,
			name: "communities___en"
		},
		{
			path: "/communities",
			component: _e32cc490,
			name: "communities___nl"
		},
		{
			path: "/en/materials/search",
			component: _70c48e2d,
			name: "materials-search___en"
		},
		{
			path: "/materialen/zoeken",
			component: _70c48e2d,
			name: "materials-search___nl"
		},
		{
			path: "/en/my/filters",
			component: _77aed046,
			name: "my-filters___en"
		},
		{
			path: "/mijn/filters",
			component: _77aed046,
			name: "my-filters___nl"
		},
		{
			path: "/en/my/collections",
			component: _169285f4,
			name: "my-collections___en"
		},
		{
			path: "/mijn/collecties",
			component: _169285f4,
			name: "my-collections___nl"
		},
		{
			path: "/en/my/collection/:id",
			component: _3729fb6e,
			name: "my-collection___en",
      meta: {
        editable: true
      }
		},
		{
			path: "/mijn/collectie/:id",
			component: _3729fb6e,
			name: "my-collection___nl",
      meta: {
        editable: true
      }
		},
		{
			path: "/en/my/communities",
			component: _b5953cb4,
			name: "my-communities___en"
		},
		{
			path: "/mijn/communities",
			component: _b5953cb4,
			name: "my-communities___nl"
		},
    {
      path: "/en/my/community/:community",
      component: myCommunity,
      name: "my-community___en"
    },
    {
      path: "/mijn/community/:community",
      component: myCommunity,
      name: "my-community___nl"
    },
		{
			path: "/en/my/filters/:id",
			component: _1c7624f6,
			name: "my-filters-id___en"
		},
		{
			path: "/mijn/filters/:id",
			component: _1c7624f6,
			name: "my-filters-id___nl"
		},
		{
			path: "/en/themes/:id",
			component: _45857c92,
			name: "themes-id___en"
		},
		{
			path: "/themas/:id",
			component: _45857c92,
			name: "themes-id___nl"
		},
		{
			path: "/en/materials/:id",
			component: _4ed33c85,
			name: "materials-id___en"
		},
		{
			path: "/materialen/:id",
			component: _4ed33c85,
			name: "materials-id___nl"
		},
		{
			path: "/en/collections/:id?",
			component: _3729fb6e,
			name: "collections-id___en",
      meta: {
			  editable: false
      }
		},
		{
			path: "/collecties/:id?",
			component: _3729fb6e,
			name: "collections-id___nl",
      meta: {
        editable: false
      }
		},
		{
			path: "/en/communities/:community",
			component: _e164c612,
			name: "communities-community___en"
		},
		{
			path: "/communities/:community",
			component: _e164c612,
			name: "communities-community___nl"
		},
		{
			path: "/en/communities/:community/search",
			component: _0624db53,
			name: "communities-community-search___en"
		},
		{
			path: "/communities/:community/zoeken",
			component: _0624db53,
			name: "communities-community-search___nl"
		},
		{
			path: "/en/communities/:community/collections/:id?",
			component: _2cdbb9b6,
			name: "communities-community-collections-id___en"
		},
		{
			path: "/communities/:community/collecties/:id?",
			component: _2cdbb9b6,
			name: "communities-community-collections-id___nl"
		},
        {
            path: "/en/privacy",
            component: infoPage,
            name: "privacy___en",
            meta: {
                title_translation_key: 'title-privacy-info',
                html_translation_key: 'html-privacy-info'
            }
        },
        {
            path: "/privacy",
            component: infoPage,
            name: "privacy___nl",
            meta: {
                title_translation_key: 'title-privacy-info',
                html_translation_key: 'html-privacy-info'
            }
        },
        {
            path: "/en/copyright",
            component: infoPage,
            name: "copyright___en",
            meta: {
                title_translation_key: 'title-copyright-info',
                html_translation_key: 'html-copyright-info'
            }
        },
        {
            path: "/copyright",
            component: infoPage,
            name: "copyright___nl",
            meta: {
                title_translation_key: 'title-copyright-info',
                html_translation_key: 'html-copyright-info'
            }
        },
        {
            path: "/en/cookies",
            component: infoPage,
            name: "cookies___en",
            meta: {
                title_translation_key: 'title-cookies-info',
                html_translation_key: 'html-cookies-info'
            }
        },
        {
            path: "/cookies",
            component: infoPage,
            name: "cookies___nl",
            meta: {
                title_translation_key: 'title-cookies-info',
                html_translation_key: 'html-cookies-info'
            }
        },
        {
            path: "/en/disclaimer",
            component: infoPage,
            name: "disclaimer___en",
            meta: {
                title_translation_key: 'title-disclaimer-info',
                html_translation_key: 'html-disclaimer-info'
            }
        },
        {
            path: "/disclaimer",
            component: infoPage,
            name: "disclaimer___nl",
            meta: {
                title_translation_key: 'title-disclaimer-info',
                html_translation_key: 'html-disclaimer-info'
            }
        },
		{
			path: "/en/",
			component: _ebbee700,
			name: "index___en"
		},
		{
			path: "/",
			component: _ebbee700,
			name: "index___nl"
		}

    ],


    fallback: false
  })
}
