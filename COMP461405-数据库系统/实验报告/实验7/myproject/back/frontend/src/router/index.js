import { createRouter, createWebHistory } from 'vue-router'
import FleetView from '../views/FleetView.vue'
import VehicleView from '../views/VehicleView.vue'
import DriverView from '../views/DriverView.vue'
import DriveView from '../views/DriveView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/fleets'
    },
    {
      path: '/fleets',
      name: 'fleets',
      component: FleetView
    },
    {
      path: '/vehicles',
      name: 'vehicles',
      component: VehicleView
    },
    {
      path: '/drivers',
      name: 'drivers',
      component: DriverView
    },
    {
      path: '/drives',
      name: 'drives',
      component: DriveView
    }
  ]
})

export default router 