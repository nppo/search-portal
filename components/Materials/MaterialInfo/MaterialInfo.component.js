import StarRating from '~/components/StarRating';
import PopularList from '~/components/Communities/PopularList';
import Themes from '~/components/Themes';
import Keywords from '~/components/Keywords';
export default {
  name: 'material-info',
  props: ['material'],
  components: {
    StarRating,
    Themes,
    PopularList,
    Keywords
  },
  mounted() {},
  data() {
    return {
      formData: {
        page_size: 10,
        page: 1,
        filters: [],
        search_text: []
      }
    };
  },
  methods: {},
  computed: {
    authorUrl() {
      if (this.material) {
        this.formData.author = this.material.author;
        return {
          path: '/materials/search/',
          query: Object.assign({}, this.formData, {
            filters: JSON.stringify(this.formData.filters),
            search_text: JSON.stringify(this.formData.search_text)
          })
        };
      }
    }
  }
};
