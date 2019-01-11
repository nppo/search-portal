import BreadCrumbs from '~/components/BreadCrumbs';
import DirectSearch from '~/components/FilterCategories/DirectSearch';
import ShareMaterialCollection from '~/components/Popup/ShareMaterialCollection';
import ShareCollection from '~/components/Popup/ShareCollection';
import DeleteCollection from '~/components/Popup/DeleteCollection';

export default {
  name: 'collection',
  props: {
    collection: {
      default: false
    },
    contenteditable: {
      default: false
    },
    setEditable: {
      default: false
    },
    submitting: {
      default: false
    },
    changeViewType: {
      default: false
    },
    'items-in-line': {
      default: 4
    },
    user: {
      default: false
    }
  },
  components: {
    BreadCrumbs,
    DirectSearch,
    ShareMaterialCollection,
    ShareCollection,
    DeleteCollection
  },
  mounted() {
    const { collection } = this;
    if (collection) {
      this.setTitle(collection.title);
      this.setSocialCounters();
    }
    this.href = window.location.href;
  },
  data() {
    return {
      href: '',
      collection_title: null,
      search: {},
      isShowShareMaterial: false,
      isShowDeleteCollection: false,
      isShowShareCollection: false,
      is_copied: false,
      is_shared: this.collection.is_shared
    };
  },
  methods: {
    /**
     * Set collection title
     * @param title - String
     */
    setTitle(title) {
      if (title) {
        this.collection_title = title;
        // if (this.$refs.title) {
        //   this.$refs.title.innerText = title;
        // }
      }
    },
    /**
     * Trigger on the change collection title
     */
    onChangeTitle() {
      if (this.$refs.title) {
        this.setTitle(this.$refs.title.innerText);
      }
    },
    /**
     * Reset changed data
     */
    resetData() {
      this.setTitle(this.collection.title);
    },
    /**
     * Deleting collection by id
     */
    deleteCollectionPopup() {
      this.isShowDeleteCollection = true;
    },
    /**
     * Deleting collection by id
     */
    deleteCollection() {
      this.$store
        .dispatch('deleteMyCollection', this.$route.params.id)
        .then(() => {
          this.$router.push(this.localePath({ name: 'my-collections' }));
        });
    },
    closeDeleteCollection() {
      this.isShowDeleteCollection = false;
    },
    /**
     * Show the popup "Share material"
     */
    showShareMaterial() {
      this.isShowShareMaterial = true;
    },
    /**
     * The change shared event
     */
    changeShared() {
      this.$store.dispatch(
        'putMyCollection',
        Object.assign({}, this.collection, { is_shared: this.is_shared })
      );
    },
    /**
     * Hide the popup "Share material"
     */
    closeShareMaterial() {
      this.isShowShareMaterial = false;
      if (this.is_copied) {
        this.closeSocialSharing('link');
      }
    },
    /**
     * Saving the collection
     */
    onSubmit() {
      this.$emit('onSubmit', { title: this.collection_title });
    },
    /**
     * Set counters value for share buttons
     */
    setSocialCounters() {
      let isSetChanges = false;
      const interval = setInterval(() => {
        this.$nextTick().then(() => {
          const { collection } = this;
          const { social_counters } = this.$refs;
          const linkedIn = social_counters.querySelector('#linkedin_counter');

          if (
            collection &&
            collection.sharing_counters &&
            social_counters &&
            linkedIn
          ) {
            const share = collection.sharing_counters.reduce(
              (prev, next) => {
                prev[next.sharing_type] = next;
                return prev;
              },
              {
                linkedin: {
                  counter_value: 0
                },
                twitter: {
                  counter_value: 0
                },
                link: {
                  counter_value: 0
                }
              }
            );

            if (share.linkedin) {
              social_counters.querySelector('#linkedin_counter').innerText =
                share.linkedin.counter_value;
            }
            if (share.twitter) {
              social_counters.querySelector('#twitter_counter').innerText =
                share.twitter.counter_value;
            }
            if (share.link) {
              social_counters.querySelector('#url_counter').innerText =
                share.link.counter_value;
            }
            if (linkedIn) {
              isSetChanges = true;
              clearInterval(interval);
            }
          }
        });
      }, 200);
    },
    /**
     * Event close social popups
     * @param type - String - social type
     */
    closeSocialSharing(type) {
      this.$store
        .dispatch('setCollectionSocial', {
          id: this.$route.params.id,
          params: {
            shared: type
          }
        })
        .then(() => {
          this.setSocialCounters();
        });
    },
    /**
     * Show the popup "Share collection"
     */
    showShareCollection() {
      this.isShowShareCollection = true;
    },
    /**
     * Close the popup "Share collection"
     */
    closeShareCollection() {
      this.isShowShareCollection = false;
      if (this.is_copied) {
        this.closeSocialSharing('link');
      }
    }
  },
  watch: {
    /**
     * Watcher on the search field
     * @param search - String
     */
    search(search) {
      this.$emit('input', search);
    },
    /**
     * Watcher on the 'collection.is_shared' field
     * @param is_shared - Boolean
     */
    'collection.is_shared'(is_shared) {
      this.is_shared = is_shared;
    },
    /**
     * Watcher on the contenteditable field
     * @param isEditable - Boolean
     */
    contenteditable(isEditable) {
      const { title } = this.$refs;
      this.$nextTick().then(() => {
        title.focus();
      });
      if (!isEditable) {
        this.resetData();
      }
    },
    /**
     * Watcher on the collection object
     * @param collection - Object
     */
    collection(collection) {
      if (collection) {
        this.setTitle(collection.title);
        this.setSocialCounters();
      }
    }
  }
};
