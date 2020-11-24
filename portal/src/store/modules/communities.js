import { isNil, isEmpty, find, filter } from 'lodash'
import injector from 'vue-inject'
import { validateID, validateParams } from './_helpers'
import { PublishStatus } from '~/utils'
import axios from '~/axios'

const $log = injector.get('$log')

export default {
  state: {
    communities: null,
    community_info: {},
    community_themes: null,
    community_disciplines: null,
    community_collections: null,
    community_collections_loading: null,
    my_community_active_tab: 0,
    communities_active_tab: 0
  },
  getters: {
    communities(state) {
      return state.communities
    },
    allCommunities(state) {
      return user => {
        if (!state.communities) {
          return []
        }

        return state.communities.filter(community => {
          return (
            community.publish_status === PublishStatus.PUBLISHED ||
            (user &&
              user.communities &&
              user.communities.indexOf(community.id) >= 0)
          )
        })
      }
    },
    userCommunities(state) {
      return user => {
        if (!state.communities || isNil(user)) {
          return []
        }
        return state.communities.filter(community => {
          return user.communities.indexOf(community.id) >= 0
        })
      }
    },
    getCommunityInfo(state) {
      return user => {
        if (isEmpty(state.community_info)) {
          return state.community_info
        } else if (
          state.community_info.publish_status === PublishStatus.PUBLISHED
        ) {
          return state.community_info
        } else if (
          user &&
          user.communities.indexOf(state.community_info.id) >= 0
        ) {
          return state.community_info
        }
      }
    },
    getCommunityDetails(state, getters) {
      return (user, language) => {
        let communityInfo = getters.getCommunityInfo(user)
        return find(communityInfo.community_details, {
          language_code: language.toUpperCase()
        })
      }
    },
    community_themes(state) {
      return state.community_themes
    },
    community_disciplines(state) {
      return state.community_disciplines
    },
    community_collections(state) {
      return state.community_collections
    },
    community_collections_loading(state) {
      return state.community_collections_loading
    },
    getPublicCollections(state) {
      return user => {
        if (!state.community_collections) {
          return []
        }
        return filter(state.community_collections.results, collection => {
          return (
            collection.publish_status === PublishStatus.PUBLISHED ||
            (user &&
              find(user.collections, { id: collection.id }) &&
              collection.publish_status !== PublishStatus.DRAFT)
          )
        })
      }
    },
    myCommunityActiveTab(state) {
      return state.my_community_active_tab
    },
    communitiesActiveTab(state) {
      return state.communities_active_tab
    }
  },
  actions: {
    async getCommunities({ commit }, { params = {} } = {}) {
      if (validateParams(params)) {
        const { data: communities } = await axios.get('communities/', {
          params
        })
        commit('SET_COMMUNITIES', communities.results)
        return communities
      } else {
        $log.error('Validate error: ', { params })
      }
    },
    async putCommunity({ commit }, { id, data = {} } = {}) {
      if (validateID(id) && validateParams(data)) {
        const { data: community } = await axios.put(`communities/${id}/`, data)
        commit('UPDATE_COMMUNITY', community)
        return community
      } else {
        $log.error('Validate error: ', { id, data })
      }
    },
    async getCommunity({ commit }, id) {
      if (validateID(id)) {
        const { data: communityInfo } = await axios.get(`communities/${id}/`)
        commit('SET_COMMUNITY', communityInfo)
      } else {
        $log.error('Validate error: ', id)
      }
    },
    async getCommunityThemes({ commit }, id) {
      if (validateID(id)) {
        const { data: communityThemes } = await axios.get(
          `communities/${id}/themes/`
        )
        commit('SET_COMMUNITY_THEMES', communityThemes)
      } else {
        $log.error('Validate error: ', id)
      }
    },
    async getCommunityDisciplines({ commit }, id) {
      if (validateID(id)) {
        const { data: communityDisciplines } = await axios.get(
          `communities/${id}/disciplines/`
        )
        commit('SET_COMMUNITY_DISCIPLINES', communityDisciplines)
      } else {
        $log.error('Validate error: ', id)
      }
    },
    async getCommunityCollections({ commit }, id) {
      if (validateID(id)) {
        commit('SET_COMMUNITY_COLLECTIONS_LOADING', true)
        const { data: communityCollections } = await axios.get(
          `communities/${id}/collections/`
        )
        commit('SET_COMMUNITY_COLLECTIONS', communityCollections)
        commit('SET_COMMUNITY_COLLECTIONS_LOADING', false)
      } else {
        $log.error('Validate error: ', id)
      }
    },
    async getCommunityCollectionsNextPage({ commit, state }) {
      commit('SET_COMMUNITY_COLLECTIONS_LOADING', true)
      const { data: communityCollections } = await axios.get(
        state.community_collections.next
      )

      commit('SET_COMMUNITY_COLLECTIONS_NEXT', communityCollections)
      commit('SET_COMMUNITY_COLLECTIONS_LOADING', false)
    },
    async postCommunityCollection({ commit }, data) {
      if (validateParams(data)) {
        const { data: collection } = await axios.post(`collections/`, data)
        commit('ADD_COMMUNITY_COLLECTION', collection)
        return collection
      } else {
        $log.error('Validate error: ', data)
      }
    },
    async deleteCommunityCollections(context, { id, data }) {
      if (validateParams(data)) {
        await axios.delete(`communities/${id}/collections/`, { data })
      } else {
        $log.error('Validate error: ', data)
      }
    },
    async setCommunityCollection({ commit }, { id, data }) {
      if (validateID(id) && validateParams(data)) {
        const { data: communityCollections } = await axios.post(
          `communities/${id}/collections/`,
          data
        )

        commit('EXTEND_COMMUNITY_COLLECTION', communityCollections)
        return communityCollections
      } else {
        $log.error('Validate error: ', { id, data })
      }
    }
  },
  mutations: {
    SET_COMMUNITIES(state, payload) {
      state.communities = payload
    },
    UPDATE_COMMUNITY(state, payload) {
      state.communities = state.communities.map(community => {
        if (payload.id === community.id) {
          return payload
        }

        return community
      })
    },
    SET_COMMUNITY(state, payload) {
      state.community_info = payload
    },
    SET_COMMUNITY_DISCIPLINES(state, payload) {
      state.community_disciplines = payload
    },
    SET_COMMUNITY_THEMES(state, payload) {
      state.community_themes = payload
    },
    SET_COMMUNITY_COLLECTIONS(state, payload) {
      state.community_collections = payload
    },
    SET_COMMUNITY_COLLECTIONS_NEXT(state, payload) {
      state.community_collections = {
        ...state.community_collections,
        next: payload.next,
        results: [...state.community_collections.results, ...payload.results]
      }
    },
    ADD_COMMUNITY_COLLECTION(state, payload) {
      const results = state.community_collections.results || []
      state.community_collections = {
        ...state.community_collections,
        results: [payload, ...results]
      }
    },
    EXTEND_COMMUNITY_COLLECTION(state, payload) {
      const results = state.community_collections.results || []
      const payloadItem = payload[0]

      state.community_collections = {
        ...state.community_collections,
        results: results.map(item => {
          if (item.id === payloadItem.id) {
            return payloadItem
          }
          return item
        })
      }
    },
    SET_COMMUNITY_COLLECTIONS_LOADING(state, payload) {
      state.community_collections_loading = payload
    },
    SET_MY_COMMUNITY_ACTIVE_TAB(state, payload) {
      state.my_community_active_tab = payload
    },
    SET_COMMUNITIES_ACTIVE_TAB(state, payload) {
      state.communities_active_tab = payload
    }
  }
}
