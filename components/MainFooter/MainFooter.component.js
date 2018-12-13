import Menu from './Menu';
import { mapGetters } from 'vuex';

export default {
  name: 'main-footer',
  props: [],
  components: {
    Menu
  },
  mounted() {},
  data() {
    return {
      isShowSubMenu: this.show_sub_menu
    };
  },
  methods: {
    toggleSubMenuThemes() {
      console.log('footer', this.isShowSubMenu);
      this.isShowSubMenu = !this.isShowSubMenu;
      this.$store.dispatch('setSubMenuShow', this.isShowSubMenu);
    }
  },
  watch: {
    show_sub_menu(show_sub_menu) {
      this.isShowSubMenu = show_sub_menu;
    }
  },
  computed: {
    ...mapGetters(['show_sub_menu'])
  }
};
