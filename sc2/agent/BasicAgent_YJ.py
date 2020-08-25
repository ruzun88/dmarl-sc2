from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from absl import app
import random
import time


class TerranBasicAgent(base_agent.BaseAgent):
    def __init__(self):
        super(TerranBasicAgent, self).__init__()

        self.base_top_left = None
        self.supply_depot_built = False
        self.supply_depot_built_2 = False
        self.barracks_built = False
        self.barracks_rallied = False
        self.army_rallied = False
        self.factories_built = False
        self.factories_rallied = False
        self.refineries_built = False
        self.refineries_coord = []
        self.enough_scv = False


    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]

        return [x + x_distance, y + y_distance]

    def getMeanLocation(self, unitList):
        sum_x = 0
        sum_y = 0
        for unit in unitList:
            sum_x += unit.x
            sum_y += unit.y
        mean_x = sum_x / len(unitList)
        mean_y = sum_y / len(unitList)

        return [mean_x, mean_y]

    def unit_type_is_selected(self, obs, unit_type):
        if (len(obs.observation.single_select) > 0 and
                obs.observation.single_select[0].unit_type == unit_type):
            return True

        if (len(obs.observation.multi_select) > 0 and
                obs.observation.multi_select[0].unit_type == unit_type):
            return True

        return False

    def get_units_by_type(self, obs, unit_type):
        return [unit for unit in obs.observation.feature_units
                if unit.unit_type == unit_type]

    def can_do(self, obs, action):
        return action in obs.observation.available_actions

    def get_refineries_coordinates(self, obs):
        gases = self.get_units_by_type(obs, units.Neutral.VespeneGeyser)
        return [[unit.x, unit.y] for unit in gases]


    def step(self, obs):
        super(TerranBasicAgent, self).step(obs)

        # time.sleep(0.5)

        if obs.first():
            self.base_top_left = None
            self.supply_depot_built = False
            self.barracks_built = False
            self.barracks_rallied = False
            self.army_rallied = False
            # print(self.refineries_coord)
            player_y, player_x = (
                    obs.observation.feature_minimap.player_relative == features.PlayerRelative.SELF).nonzero()
            self.base_top_left = 1 if player_y.any() and player_y.mean() <= 31 else 0
        if not self.refineries_built:
            self.refineries_coord = self.get_refineries_coordinates(obs)
            if self.unit_type_is_selected(obs, units.Terran.SCV):
                if self.can_do(obs, actions.FUNCTIONS.Build_Refinery_screen.id):
                    ccs = self.get_units_by_type(obs, units.Terran.CommandCenter)
                    if len(ccs) > 0 and len(self.refineries_coord) > 0:
                        self.refineries_built = True
                        return actions.FUNCTIONS.Build_Refinery_screen("now", self.refineries_coord[0])
            scvs = self.get_units_by_type(obs, units.Terran.SCV)
            if len(scvs) > 0:
                scv = random.choice(scvs)
                return actions.FUNCTIONS.select_point("select", (scv.x,
                                                                 scv.y))

        if not self.enough_scv:
            if len(self.get_units_by_type(obs, units.Terran.SCV)) >= 15:
                self.enough_scv = True
            ccs = self.get_units_by_type(obs, units.Terran.CommandCenter)
            cmd1 = random.choice(ccs)
            if not self.unit_type_is_selected(obs, units.Terran.CommandCenter):
                return actions.FUNCTIONS.select_point("select", (cmd1.x, cmd1.y))
            if self.can_do(obs, actions.FUNCTIONS.Train_SCV_quick.id):
                return actions.FUNCTIONS.Train_SCV_quick("queued")

        if not self.supply_depot_built:
            if self.unit_type_is_selected(obs, units.Terran.SCV):
                if self.can_do(obs, actions.FUNCTIONS.Build_SupplyDepot_screen.id):
                    ccs = self.get_units_by_type(obs, units.Terran.CommandCenter)
                    if len(ccs) > 0:
                        mean_x, mean_y = self.getMeanLocation(ccs)
                        target = self.transformLocation(int(mean_x), 20, int(mean_y), 0)
                        self.supply_depot_built = True

                        return actions.FUNCTIONS.Build_SupplyDepot_screen("now", target)
            scvs = self.get_units_by_type(obs, units.Terran.SCV)
            if len(scvs) > 0:
                scv = random.choice(scvs)
                return actions.FUNCTIONS.select_point("select", (scv.x,
                                                                 scv.y))
        elif not self.supply_depot_built_2:
            if self.unit_type_is_selected(obs, units.Terran.SCV):
                if self.can_do(obs, actions.FUNCTIONS.Build_SupplyDepot_screen.id):
                    ccs = self.get_units_by_type(obs, units.Terran.CommandCenter)
                    if len(ccs) > 0:
                        mean_x, mean_y = self.getMeanLocation(ccs)
                        target = self.transformLocation(int(mean_x), 0, int(mean_y), 15)
                        self.supply_depot_built_2 = True

                        return actions.FUNCTIONS.Build_SupplyDepot_screen("now", target)
            scvs = self.get_units_by_type(obs, units.Terran.SCV)
            if len(scvs) > 0:
                scv = random.choice(scvs)
                return actions.FUNCTIONS.select_point("select", (scv.x,
                                                                 scv.y))

        if not self.barracks_built:
            if self.unit_type_is_selected(obs, units.Terran.SCV):
                if self.can_do(obs, actions.FUNCTIONS.Build_Barracks_screen.id):
                    sd = self.get_units_by_type(obs, units.Terran.SupplyDepot)
                    if len(sd) > 0:
                        mean_x, mean_y = self.getMeanLocation(sd)
                        target = self.transformLocation(int(mean_x), 12, int(mean_y), 0)
                        self.barracks_built = True

                        return actions.FUNCTIONS.Build_Barracks_screen("now", target)
            scvs = self.get_units_by_type(obs, units.Terran.SCV)
            if len(scvs) > 0:
                scv = random.choice(scvs)
                return actions.FUNCTIONS.select_point("select", (scv.x,
                                                                 scv.y))
        elif not self.factories_built:
            if self.unit_type_is_selected(obs, units.Terran.SCV):
                if self.can_do(obs, actions.FUNCTIONS.Build_Factory_screen.id):
                    sd = self.get_units_by_type(obs, units.Terran.SupplyDepot)
                    if len(sd) > 0:
                        mean_x, mean_y = self.getMeanLocation(sd)
                        target = self.transformLocation(int(mean_x), 0, int(mean_y), 12)
                        self.factories_built = True

                        return actions.FUNCTIONS.Build_Factory_screen("now", target)
            scvs = self.get_units_by_type(obs, units.Terran.SCV)
            if len(scvs) > 0:
                scv = random.choice(scvs)
                return actions.FUNCTIONS.select_point("select", (scv.x,
                                                                 scv.y))

        elif not self.factories_rallied:
            if self.unit_type_is_selected(obs, units.Terran.Factory):
                self.factories_rallied = True

                if self.base_top_left:
                    return actions.FUNCTIONS.Rally_Units_minimap("now", [29, 21])
                else:
                    return actions.FUNCTIONS.Rally_Units_minimap("now", [29, 46])
            factories = self.get_units_by_type(obs, units.Terran.Factory)
            if len(factories) > 0:
                factory = random.choice(factories)
                return actions.FUNCTIONS.select_point("select", (factory.x,
                                                                 factory.y))

        elif obs.observation.player.food_cap - obs.observation.player.food_used > 1:
            if self.can_do(obs, actions.FUNCTIONS.Train_Hellion_quick.id):
                return actions.FUNCTIONS.Train_Hellion_quick("queued")

        elif not self.army_rallied:
            if self.can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
                self.army_rallied = True

                if self.base_top_left:
                    return actions.FUNCTIONS.Attack_minimap("now", [39, 45])
                else:
                    return actions.FUNCTIONS.Attack_minimap("now", [21, 24])

            if self.can_do(obs, actions.FUNCTIONS.select_army.id):
                return actions.FUNCTIONS.select_army("select")

        else:
            while True:
                if not self.unit_type_is_selected(obs, units.Terran.Factory):
                    factories = self.get_units_by_type(obs, units.Terran.Factory)
                    if len(factories) > 0:
                        factory = random.choice(factories)
                        return actions.FUNCTIONS.select_point("select", (factory.x,
                                                                         factory.y))


                elif obs.observation.player.food_cap - obs.observation.player.food_used > 1:
                    self.army_rallied = False
                    if self.can_do(obs, actions.FUNCTIONS.Train_Hellion_quick.id):
                        return actions.FUNCTIONS.Train_Hellion_quick("queued")

                elif not self.army_rallied:
                    if self.can_do(obs, actions.FUNCTIONS.Attack_minimap.id):
                        self.army_rallied = True

                        if self.base_top_left:
                            return actions.FUNCTIONS.Attack_minimap("now", [39, 45])
                        else:
                            return actions.FUNCTIONS.Attack_minimap("now", [21, 24])

                    if self.can_do(obs, actions.FUNCTIONS.select_army.id):
                        return actions.FUNCTIONS.select_army("select")
                return actions.FUNCTIONS.no_op()
        return actions.FUNCTIONS.no_op()

def main(unused_argv):
    agent = TerranBasicAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                    #map_name="AbyssalReef",
                    map_name="Simple64",
                    #players=[sc2_env.Agent(sc2_env.Race.zerg),
                    players=[sc2_env.Agent(sc2_env.Race.terran),
                             sc2_env.Bot(sc2_env.Race.random,
                                         sc2_env.Difficulty.very_easy)],
                    agent_interface_format=features.AgentInterfaceFormat(
                      feature_dimensions=features.Dimensions(screen=84, minimap=64),
                      use_feature_units=True),
                    step_mul=1,
                    game_steps_per_episode=0,
                    visualize=True) as env:

              agent.setup(env.observation_spec(), env.action_spec())

              timesteps = env.reset()
              agent.reset()

              while True:
                  step_actions = [agent.step(timesteps[0])]
                  if timesteps[0].last():
                      break
                  timesteps = env.step(step_actions)

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    app.run(main)
