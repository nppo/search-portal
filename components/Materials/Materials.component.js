import { mapGetters } from 'vuex';
import StarRating from './../StarRating';

export default {
  name: 'materials',
  props: {
    materials: {
      default: false
    },
    'items-in-line': {
      type: Number,
      default: 4
    }
  },
  components: {
    StarRating
  },
  mounted() {
    this.$store.dispatch('getFilterCategories');
  },
  data() {
    return {};
  },
  methods: {},
  computed: {
    ...mapGetters(['disciplines', 'educationallevels']),
    extended_materials() {
      const { materials, disciplines, educationallevels } = this;
      console.log(materials, disciplines, educationallevels);
      if (materials && disciplines && educationallevels) {
        return materials.records.map(material => {
          return Object.assign({}, material, {
            disciplines: material.disciplines.reduce((prev, id) => {
              const item = disciplines.items[id];

              if (item) {
                prev.push(item);
              }

              return prev;
            }, []),
            educationallevels: material.educationallevels.reduce((prev, id) => {
              const item = educationallevels.items[id];

              if (item) {
                prev.push(item);
              }

              return prev;
            }, [])
          });
        });
      }

      return false;
    }
  }
};
