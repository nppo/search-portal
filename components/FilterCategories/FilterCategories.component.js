import { mapGetters } from 'vuex';
import { generateSearchMaterialsQuery } from '../_helpers';
import DatesRange from '~/components/DatesRange';
import _ from 'lodash';


export default {
  name: 'filter-categories',
  props: ['showPopupSaveFilter', 'full-filter'],
  components: { DatesRange },
  mounted() {
    if (this.isAuthenticated && !this.fullFilter) {
      this.$store.dispatch('getFilters');
    }
  },
  data() {
    const publisherdate = 'lom.lifecycle.contribute.publisherdate';
    return {
      publisherdate,
      selected: [],
      show_all: [],
      isShow: false,
      isInit: false,
      visible_items: 20,
      data: {
        start_date: null,
        end_date: null
      },
      categoryItemsById: {}
    };
  },
  methods: {
    generateSearchMaterialsQuery,
    hasVisibleChildren(category) {
      if(!category.children.length) {
        return false;
      }
      return _.some(category.children, (child) => { return !child.is_hidden; })
    },
    setChildrenSelected(children, value) {
      _.forEach(children, (child) => {
        child.selected = value;
        this.setChildrenSelected(child.children, value);
      });
    },
    onToggleCategory(category, update = true) {
      category.isOpen = !category.isOpen;
      _.forEach(category.children, (child) => { this.onToggleCategory(child, false); } );
      if(update) {
        this.$forceUpdate();
      }
    },
    onToggleShowAll(category) {
      category.show_all = !category.show_all;
      this.$forceUpdate();
    },
    /**
     * Set filter for v-model
     * @returns {*} - filters
     */
    setFilter() {
      const { categories, filter, publisherdate } = this;
      if (filter && categories) {
        let filters = filter.reduce((prev, next) => {
          const hasItems = next.items.find(item => item);
          if (hasItems) {
            prev.push({
              external_id: next.external_id,
              items: next.items.reduce((prevChild, nextChild, index) => {
                if (nextChild) {
                  const category = categories.results.find(
                    category => category.external_id === next.external_id
                  );
                  prevChild.push(category.items[index].external_id);
                }
                return prevChild;
              }, [])
            });
          }
          return prev;
        }, []);

        const publisherdate_item = this.value.filters.find(
          item => item.external_id === publisherdate
        );

        if (publisherdate_item) {
          filters.push({
            external_id: publisherdate,
            items: [...publisherdate_item.items]
          });
          this.data = {
            start_date: publisherdate_item.items[0],
            end_date: publisherdate_item.items[1]
          };
        }

        filters = Object.assign({}, this.value, {
          filters
        });

        this.$router.push(this.generateSearchMaterialsQuery(filters));

        this.$emit('input', filters);

        return filters;
      }
    },
    loadCategoryItems(items, parent) {
      let parentSelected = (_.isNull(parent)) ? false : parent.selected || parent.enabled_by_default;
      let searchId = (_.isNull(parent)) ? null : parent.searchId;
      _.forEach(items, (item) => {

        // Load all items into their own lookup table
        this.categoryItemsById[item.id] = item;
        // Set relevant properties for date filters
        if(item.external_id === this.publisherdate) {
          item.dates = {
            start_date: null,
            end_date: null
          }
        }
        // Set values that might be relevant when loading children
        item.searchId = searchId || item.external_id;
        item.selected = parentSelected || item.enabled_by_default;
        // Load children and retrospecively set some parent properties
        let hasSelectedChildren = this.loadCategoryItems(item.children, item);
        item.show_all = false;
        item.selected = item.isOpen = item.selected || hasSelectedChildren;
      });
      return _.some(items, (item) => { return item.selected; });
    },
    getFiltersForSearch(items) {
      return _.reduce(items, (results, item) => {
        // Recursively find selected filters for the children
        if(item.children.length) {
            results = results.concat(this.getFiltersForSearch(item.children));
        }
        // Add this filter if it is selected
        if(item.selected && !_.isNull(item.parent)) {
          results.push(item);
        }
        // Also add this filter if a date has been selected
        if(item.external_id === this.publisherdate && (item.dates.start_date || item.dates.end_date)) {
          results.push(item);
        }
        return results;
      }, []);
    },
    onChange(event) {

      // Recursively update selections
      let changedCategory = this.categoryItemsById[event.target.dataset.categoryId];
      if(!_.isNil(changedCategory)) {
        this.setChildrenSelected(changedCategory.children, changedCategory.selected);
        this.$forceUpdate();
      }

      this.executeSearch();

    },
    onDateChange(dates) {
      this.executeSearch();
    },
    executeSearch() {
      const { filter_categories } = this;

      // Create the search request from the current selection and stored data
      let selected = this.getFiltersForSearch(filter_categories.results);
      let selectedGroups = _.groupBy(selected, 'searchId');
      let filters = _.map(selectedGroups, (items, group) => {
        if(group === this.publisherdate) {
          let dates = items[0].dates;
          return {
            external_id: group,
            items: [dates.start_date || null, dates.end_date || null]
          }
        }
        return {
            external_id: group,
            items: _.reject(
                _.map(items, 'external_id'),
                _.isEmpty
            )
        }
      });
      let searchText = this.$store.getters.materials.search_text;
      let ordering = this.$store.getters.materials.ordering;
      let searchRequest = {
          search_text: searchText,
          ordering: ordering,
          filters: filters
      };

      // Execute search
      this.$router.push(this.generateSearchMaterialsQuery(searchRequest));
      this.$store.dispatch('searchMaterials', searchRequest);

    },
    /**
     * Get the full filter info
     * @param e - event
     */
    onFilterSelected(e) {
      this.$store.dispatch('getFilter', { id: e.target.value });
    },
    /**
     * Event the reset filter
     */
    resetFilter() {
      this.$router.push(
        this.generateSearchMaterialsQuery({
          search_text: this.value.search_text
        })
      );
      this.$nextTick().then(() => {
        location.reload();
      });
    },
    isShowCategoryItem({ category, item, indexItem }) {
      return (
        !item.is_empty && (category.show_all || indexItem < this.visible_items)
      );
    },
    getTitleTranslation( category, language ) {
      if (!_.isNil(category.title_translations) && !_.isEmpty(category.title_translations)){
        return category.title_translations[language];
      }
      return category.name
    }
  },
  watch: {
    data(data) {
      let { publisherdate } = this;
      let filters = this.value.filters.slice(0);

      const publisherdate_item = filters.find(
        item => item.external_id === publisherdate
      );

      if (publisherdate_item) {
        filters = filters.map(item => {
          if (item.external_id === publisherdate) {
            return {
              external_id: publisherdate,
              items: [data.start_date || null, data.end_date || null]
            };
          }
          return item;
        });
      } else {
        filters.push({
          external_id: publisherdate,
          items: [data.start_date || null, data.end_date || null]
        });
      }

      const request = Object.assign({}, this.value, { filters });

      this.$emit('input', request);
      this.$router.push(this.generateSearchMaterialsQuery(request));
    },
    /**
     * Watcher on change user authentication
     * @param isAuthenticated
     */
    isAuthenticated(isAuthenticated) {
      if (isAuthenticated && !this.fullFilter) {
        this.$store.dispatch('getFilters');
      }
    },
    /**
     * Generating search query on change the active filter
     * @param active_filter
     */
    active_filter(active_filter) {
      const { filter_categories, publisherdate, value } = this;
      if (active_filter && active_filter.items && filter_categories) {
        const publisherdate_item = filter_categories.results.find(
          item => item.external_id === publisherdate
        );
        const normailze_filter = active_filter.items.reduce((prev, next) => {
          prev[next.category_id] = prev[next.category_id] || [];
          prev[next.category_id].push(next.category_item_id);
          return prev;
        }, {});
        const filters = filter_categories.results.reduce(
          (search, category) => {
            const category_items = normailze_filter[category.id];
            if (category_items) {
              search.filters.push({
                external_id: category.external_id,
                items: category.items
                  .filter(item => category_items.indexOf(item.id) !== -1)
                  .map(item => item.external_id)
              });
            }
            return search;
          },
          {
            page: 1,
            page_size: value.page_size,
            filters: [
              {
                external_id: publisherdate_item.external_id,
                items: [active_filter.start_date, active_filter.end_date]
              }
            ],
            search_text: active_filter.search_text || value.search_text || []
          }
        );

        this.$router.push(this.generateSearchMaterialsQuery(filters));

        this.$emit('input', filters);
      }
    }
  },
  computed: {
    ...mapGetters([
      'filter_categories',
      'isAuthenticated',
      'filters',
      'active_filter',
      'materials'
    ]),
    active_filter_id() {
      const { active_filter } = this;
      if (active_filter) {
        return active_filter.id || '';
      }

      return '';
    },
    /**
     * generate filter items
     * @returns {*}
     */
    filter() {
      const { value, filtered_categories } = this;
      if (value && value.filters && filtered_categories) {
        const filter = value.filters.reduce((prev, next) => {
          prev[next.external_id] = next;

          return prev;
        }, {});

        return filtered_categories.map(item => {
          const current_item = filter[item.external_id];

          return current_item && current_item.items
            ? Object.assign({}, current_item, {
                items: item.children.map(
                  el => current_item.items.indexOf(el.external_id) !== -1
                )
              })
            : Object.assign({}, item, { items: [] });
        });
      }

      return false;
    },
    /**
     * generate filtered categories
     * @returns {*}
     */
    filtered_categories() {
      const { filter_categories } = this;
      if (filter_categories) {
        this.loadCategoryItems(filter_categories.results, null);
        return filter_categories.results;
      }
      return [];
    },
    /**
     * generate extending categories
     * @returns {*}
     */
    categories() {
      const { selected, show_all, filtered_categories, materials } = this;
      if (selected && filtered_categories && materials && materials.filters) {
        const not_empty_ids = materials.filters.reduce((prev, next) => {
          prev.push(...next.items.map(item => item.external_id));
          return prev;
        }, []);

        return Object.assign({}, filtered_categories, {
          results: filtered_categories.map(category => {
            return Object.assign({}, category, {
              selected: selected.indexOf(category.external_id) !== -1,
              show_all: show_all.indexOf(category.id) !== -1,
              items: [
                ...category.children.map(item => {
                  return {
                    ...item,
                    is_empty: not_empty_ids.indexOf(item.external_id) === -1
                  };
                })
              ]
            });
          })
        });
      }
      return false;
    }
  }
};
