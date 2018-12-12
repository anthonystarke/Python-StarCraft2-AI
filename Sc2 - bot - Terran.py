import sc2
from sc2 import run_game, maps, Race, Difficulty, position
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, GATEWAY,ZEALOT,ASSIMILATOR,CYBERNETICSCORE,STALKER,PHOTONCANNON,FORGE,STARGATE,DARKSHRINE,VOIDRAY,TWILIGHTCOUNCIL,DARKTEMPLAR, \
OBSERVER, ROBOTICSFACILITY,RESEARCH_PROTOSSGROUNDWEAPONS,RESEARCH_PROTOSSGROUNDARMOR,RESEARCH_PROTOSSSHIELDS,RESEARCH_PROTOSSAIRARMOR,RESEARCH_PROTOSSAIRWEAPONS
from random import randint
import random

class SentdeBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_PROBES = 80
        self.ADVANCED_UNITS = False
        self.ATTACKED = False
        self.BUILDING_COUNTER = 0
        self.MOVE_TIMER = 0
        self.PENDING_PYLONS = 0
        self.RETURN_TO_BASE = True
        self.RETURN_TO_BASE_TIMER = 0
        self.ENEMY_UNITS_VISIBLE = False
        self.ATTACK_UNITS = 0
        self.WEAPONS_UPGRADE = 0
        self.ARMOR_UPGRADE = 0
        self.SHIELD_UPGRADE = 0

        self.AIR_WEAPONS_UPGRADE = 0
        self.AIR_ARMOR_UPGRADE = 0
        # print(dir(sc2.constants))

    async def on_step(self, iteration):

        # what to do every step
        self.iteration = iteration
        if self.MOVE_TIMER == 0:
            self.MOVE_TIMER = self.time

        if self.RETURN_TO_BASE_TIMER == 0:
            self.RETURN_TO_BASE_TIMER = self.time

        await self.scout()
        await self.distribute_workers()  # in sc2/bot_ai.py
        await self.build_workers()  # workers bc obviously
        await self.build_pylons()  # pylons are protoss supply buildings
        await self.build_assimilator()  # getting gas
        await self.expand()

        # for upgrade in self.state.upgrades:
        #     print(upgrade)

        # if len(self.units(NEXUS).ready) > 1 or self.minerals > 280:

        await self.offensive_force_buildings()
        await self.build_offensive_force()

        if len(self.units(NEXUS).ready) > 1 and self.ATTACK_UNITS > 5:
            await self.upgrade_system()

        await self.Attack_units_counter()

        if self.ATTACK_UNITS > 0:
            await self.attack()

    async def upgrade_system(self):
        if self.units(FORGE).ready.noqueue and self.WEAPONS_UPGRADE < 3:
            if self.can_afford(RESEARCH_PROTOSSGROUNDWEAPONS) and self.WEAPONS_UPGRADE == 0:
                for f in self.units(FORGE).ready.noqueue:
                    await self.do(f(RESEARCH_PROTOSSGROUNDWEAPONS))
                    self.WEAPONS_UPGRADE = 1
            elif self.can_afford(RESEARCH_PROTOSSGROUNDWEAPONS) and self.WEAPONS_UPGRADE == 1 and self.units(TWILIGHTCOUNCIL).ready  :
                for f in self.units(FORGE).ready.noqueue:
                    await self.do(f(RESEARCH_PROTOSSGROUNDWEAPONS))
                    self.WEAPONS_UPGRADE == 2
            elif self.can_afford(RESEARCH_PROTOSSGROUNDWEAPONS) and self.WEAPONS_UPGRADE == 2 and self.units(TWILIGHTCOUNCIL).ready  :
                for f in self.units(FORGE).ready.noqueue:
                    await self.do(f(RESEARCH_PROTOSSGROUNDWEAPONS))
                    self.WEAPONS_UPGRADE == 3

        if self.units(FORGE).ready.noqueue and self.ARMOR_UPGRADE < 3:
            if self.can_afford(RESEARCH_PROTOSSGROUNDARMOR) and self.ARMOR_UPGRADE == 0  :
                for f in self.units(FORGE).ready.noqueue:
                    await self.do(f(RESEARCH_PROTOSSGROUNDARMOR))
                    self.ARMOR_UPGRADE = 1
            elif self.can_afford(RESEARCH_PROTOSSGROUNDARMOR) and self.ARMOR_UPGRADE == 1 and self.units(TWILIGHTCOUNCIL).ready  :
                for f in self.units(FORGE).ready.noqueue:
                    await self.do(f(RESEARCH_PROTOSSGROUNDARMOR))
                    self.ARMOR_UPGRADE == 2
            elif self.can_afford(RESEARCH_PROTOSSGROUNDARMOR) and self.ARMOR_UPGRADE == 2 and self.units(TWILIGHTCOUNCIL).ready  :
                for f in self.units(FORGE).ready.noqueue:
                    await self.do(f(RESEARCH_PROTOSSGROUNDARMOR))
                    self.ARMOR_UPGRADE == 3

        if self.units(FORGE).ready.noqueue and self.SHIELD_UPGRADE < 3:
            if self.can_afford(RESEARCH_PROTOSSSHIELDS) and self.SHIELD_UPGRADE == 0  :
                for f in self.units(FORGE).ready.noqueue:
                    await self.do(f(RESEARCH_PROTOSSSHIELDS))
                    self.SHIELD_UPGRADE = 1
            elif self.can_afford(RESEARCH_PROTOSSSHIELDS) and self.SHIELD_UPGRADE == 1 and self.units(TWILIGHTCOUNCIL).ready  :
                for f in self.units(FORGE).ready.noqueue:
                    await self.do(f(RESEARCH_PROTOSSSHIELDS))
                    self.SHIELD_UPGRADE == 2
            elif self.can_afford(RESEARCH_PROTOSSSHIELDS) and self.SHIELD_UPGRADE == 2 and self.units(TWILIGHTCOUNCIL).ready  :
                for f in self.units(FORGE).ready.noqueue:
                    await self.do(f(RESEARCH_PROTOSSSHIELDS))
                    self.SHIELD_UPGRADE == 3

        if self.units(CYBERNETICSCORE).ready.noqueue and self.AIR_WEAPONS_UPGRADE < 3:
            if self.can_afford(RESEARCH_PROTOSSAIRARMOR) and self.AIR_WEAPONS_UPGRADE == 0 :
                for cc in self.units(CYBERNETICSCORE).ready.noqueue:
                    await self.do(cc(RESEARCH_PROTOSSAIRARMOR))
                    self.AIR_WEAPONS_UPGRADE = 1
            elif self.can_afford(RESEARCH_PROTOSSAIRARMOR) and self.AIR_WEAPONS_UPGRADE == 1 and self.units(TWILIGHTCOUNCIL).ready :
                for cc in self.units(CYBERNETICSCORE).ready.noqueue:
                    await self.do(cc(RESEARCH_PROTOSSAIRARMOR))
                    self.AIR_WEAPONS_UPGRADE == 2
            elif self.can_afford(RESEARCH_PROTOSSAIRARMOR) and self.AIR_WEAPONS_UPGRADE == 2 and self.units(TWILIGHTCOUNCIL).ready :
                for cc in self.units(CYBERNETICSCORE).ready.noqueue:
                    await self.do(cc(RESEARCH_PROTOSSAIRARMOR))
                    self.AIR_WEAPONS_UPGRADE == 3

        if self.units(CYBERNETICSCORE).ready.noqueue and self.AIR_ARMOR_UPGRADE < 3:
            if self.can_afford(RESEARCH_PROTOSSAIRWEAPONS) and self.AIR_ARMOR_UPGRADE == 0 :
                for cc in self.units(CYBERNETICSCORE).ready.noqueue:
                    await self.do(cc(RESEARCH_PROTOSSAIRWEAPONS))
                    self.AIR_ARMOR_UPGRADE = 1
            elif self.can_afford(RESEARCH_PROTOSSAIRWEAPONS) and self.AIR_ARMOR_UPGRADE == 1 and self.units(TWILIGHTCOUNCIL).ready :
                for cc in self.units(CYBERNETICSCORE).ready.noqueue:
                    await self.do(cc(RESEARCH_PROTOSSAIRWEAPONS))
                    self.AIR_ARMOR_UPGRADE == 2
            elif self.can_afford(RESEARCH_PROTOSSAIRWEAPONS) and self.AIR_ARMOR_UPGRADE == 2 and self.units(TWILIGHTCOUNCIL).ready :
                for cc in self.units(CYBERNETICSCORE).ready.noqueue:
                    await self.do(cc(RESEARCH_PROTOSSAIRWEAPONS))
                    self.AIR_ARMOR_UPGRADE == 3


    async def expand(self):
        if len(self.units(NEXUS)) > 1 and len(self.units(GATEWAY)) > 1:
            if self.units(NEXUS).amount < 5 and self.can_afford(NEXUS):
                await self.expand_now()
        elif len(self.units(NEXUS)) == 1:
            if self.can_afford(NEXUS):
                await self.expand_now()

    async def scout(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready
            location = pylon.center.towards(self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)], random.randrange(5, 10))
            if len(self.units(NEXUS)) > 1:
                if len(self.units(OBSERVER)) < 3 and len(self.units(PYLON)) > 0:
                    if len(self.units(GATEWAY)) < 1 and self.units(PYLON).ready.exists and self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                        self.BUILDING_COUNTER += 1
                        await self.build(GATEWAY, near=location)
                    elif self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE) and self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        self.BUILDING_COUNTER += 1
                        await self.build(CYBERNETICSCORE, near=location)
                    elif self.units(CYBERNETICSCORE).ready.exists and not self.units(ROBOTICSFACILITY) and self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                        self.BUILDING_COUNTER += 1
                        await self.build(ROBOTICSFACILITY, near=location)
                    elif self.units(ROBOTICSFACILITY).ready.exists:
                        for rf in self.units(ROBOTICSFACILITY).ready.noqueue:
                            if self.can_afford(OBSERVER) and self.supply_left > 0:
                                await self.do(rf.train(OBSERVER))

        if len(self.units(OBSERVER)) > 0:
            for s in self.units(OBSERVER).idle:
                if s.is_idle:
                    enemy_location = self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)]
                    move_to = self.random_location_variance(enemy_location)
                    await self.do(s.move(move_to))

    def random_location_variance(self, enemy_start_location):
            x = enemy_start_location[0]
            y = enemy_start_location[1]

            x += ((random.randrange(-20, 20))/100) * enemy_start_location[0]
            y += ((random.randrange(-20, 20))/100) * enemy_start_location[1]

            if x < 0:
                x = 0
            if y < 0:
                y = 0
            if x > self.game_info.map_size[0]:
                x = self.game_info.map_size[0]
            if y > self.game_info.map_size[1]:
                y = self.game_info.map_size[1]

            go_to = position.Point2(position.Pointlike((x,y)))
            return go_to

    async def build_workers(self):
        # nexus = command center
        if self.units(PROBE).amount <= self.MAX_PROBES:
            if self.units(NEXUS).amount > 2:
                if self.units(PROBE).amount < (22 * (self.units(NEXUS).amount) - 1 ):
                    for nexus in self.units(NEXUS).ready.noqueue:
                        if self.can_afford(PROBE):
                            await self.do(nexus.train(PROBE))
            else:
                if self.units(PROBE).amount < (22 * self.units(NEXUS).amount):
                    for nexus in self.units(NEXUS).ready.noqueue:
                        if self.can_afford(PROBE):
                            await self.do(nexus.train(PROBE))

    async def build_pylons(self):

        if not self.already_pending(PYLON):
            self.PENDING_PYLONS = 0

        if len(self.units(NEXUS).ready) > 1 and len(self.units(PYLON)) < len(self.units(NEXUS).ready):
            if self.supply_left < 10 and self.supply_cap < 200:
                nexus_loc = self.units(NEXUS).ready
                if self.can_afford(PYLON) and self.PENDING_PYLONS < 2:
                    location = nexus_loc.center.towards(self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)], random.randrange(8, 13))
                    await self.build(PYLON, near=location)
                    self.PENDING_PYLONS += 1
                    return

        elif len(self.units(PYLON)) > 2:
            if self.supply_left < 10 and self.supply_cap < 200:
                pylon_loc = self.units(PYLON).ready
                if self.can_afford(PYLON) and self.PENDING_PYLONS < 2:
                    location = pylon_loc.center.towards(self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)], random.randrange(8, 13))
                    await self.build(PYLON, near=location)
                    self.PENDING_PYLONS += 1
                    return

        else:
            if self.supply_left < 10 and self.supply_cap < 200:
                if self.units(NEXUS).ready.exists:
                    nexus_loc = self.units(NEXUS).ready
                    if self.can_afford(PYLON) and self.PENDING_PYLONS < 2:
                        location = nexus_loc.center.towards(self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)], random.randrange(8, 13))
                        await self.build(PYLON, near=location)
                        self.PENDING_PYLONS += 1
                        return

    async def offensive_force_buildings(self):

        if self.units(PYLON).ready.exists: # and self.BUILDING_COUNTER < (len(self.units(NEXUS).ready) * 8):
            pylon = self.units(PYLON).ready.random

            if len(self.units(GATEWAY)) > 0 and not self.units(FORGE) and not self.already_pending(FORGE):
                await self.build(FORGE, near=pylon)
                self.BUILDING_COUNTER += 1

            if len(self.units(NEXUS)) > 2 and not self.already_pending(CYBERNETICSCORE) and len(self.units(CYBERNETICSCORE)) < 1:
                await self.build(CYBERNETICSCORE, near=pylon)
                self.BUILDING_COUNTER += 1

            if len(self.units(NEXUS).ready) > 1 or self.minerals > 300:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY) and (len(self.units(GATEWAY).ready) < (len(self.units(NEXUS).ready) * 3)):
                    await self.build(GATEWAY, near=pylon)
                    self.BUILDING_COUNTER += 1

            if len(self.units(NEXUS).ready) > 2:
                if len(self.units(GATEWAY).ready) > 1 and len(self.units(STARGATE)) < (len(self.units(NEXUS).ready) * 3) and self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                    await self.build(STARGATE, near=pylon)
                    self.BUILDING_COUNTER += 1

                if len(self.units(STARGATE).ready) > 1 and len(self.units(ROBOTICSFACILITY)) < (len(self.units(NEXUS).ready) * 2) and self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                    await self.build(ROBOTICSFACILITY, near=pylon)
                    self.BUILDING_COUNTER += 1

                if len(self.units(STARGATE).ready) > 1 and not self.units(TWILIGHTCOUNCIL) and not self.already_pending(TWILIGHTCOUNCIL):
                    await self.build(TWILIGHTCOUNCIL, near=pylon)
                    self.BUILDING_COUNTER += 1

                if self.units(TWILIGHTCOUNCIL).ready.exists and not self.units(DARKSHRINE) and not self.already_pending(DARKSHRINE):
                    await self.build(DARKSHRINE, near=pylon)
                    self.BUILDING_COUNTER += 1

    async def offensive_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(FORGE).ready.exists:
                if self.units(PHOTONCANNON).amount < (self.units(NEXUS).amount * 2):
                    if self.can_afford(PHOTONCANNON):
                        await self.build(PHOTONCANNON, near=pylon)
            else:
                if not self.units(FORGE).ready.exists and not self.already_pending(FORGE):
                    if self.can_afford(FORGE):
                        await self.build(FORGE, near=pylon)

    async def build_offensive_force(self):
        for gw in self.units(GATEWAY).ready.noqueue:
            if len(self.units(NEXUS)) < 2:
                if self.can_afford(ZEALOT) and self.supply_left > 0:
                    await self.do(gw.train(ZEALOT))
            else:
                if not self.units(CYBERNETICSCORE):
                    if self.can_afford(ZEALOT) and self.supply_left > 0:
                        await self.do(gw.train(ZEALOT))
                else:
                    # if self.units(ZEALOT).amount > len(self.units(NEXUS).ready) * 1:
                    if self.can_afford(STALKER) and self.supply_left > 0 and len(self.units(STALKER)) < len(self.units(NEXUS)) * 5:
                            await self.do(gw.train(STALKER))
                    elif self.units(ZEALOT).amount < len(self.units(NEXUS).ready) * 5:
                        if self.can_afford(ZEALOT) and self.supply_left > 0:
                            await self.do(gw.train(ZEALOT))

                for sg in self.units(STARGATE).ready.noqueue:
                    if self.can_afford(VOIDRAY) and self.supply_left > 0:
                        await self.do(sg.train(VOIDRAY))

                for gw in self.units(GATEWAY).ready.noqueue:
                    if self.units(DARKSHRINE).ready.exists:
                        if self.can_afford(DARKTEMPLAR) and self.supply_left > 0:
                            await self.do(gw.train(DARKTEMPLAR))

    async def build_assimilator(self):
        if len(self.units(PYLON)) > 0:
            for nexus in self.units(NEXUS).ready:
                vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
                for vaspene in vaspenes:
                    if not self.can_afford(ASSIMILATOR):
                        break
                    worker = self.select_build_worker(vaspene.position)
                    if worker is None:
                        break
                    if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                        await self.do(worker.build(ASSIMILATOR, vaspene))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            if len(self.enemy_start_locations) > 1:
                return self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)]
            else:
                return self.enemy_start_locations[0]

    async def Attack_units_counter(self):
        self.ATTACK_UNITS = len(self.units(ZEALOT)) + len(self.units(STALKER)) + len(self.units(VOIDRAY)) + len(self.units(DARKTEMPLAR))

    async def attack(self):

        nexus_loc = self.units(NEXUS).ready.closest_to(self.game_info.map_center)

        if (self.time - self.RETURN_TO_BASE_TIMER) > 2:
            self.RETURN_TO_BASE_TIMER = self.time
            count_of_visible_enemies = 0

            if self.ATTACK_UNITS < 30:

                for enemy in self.known_enemy_units.closer_than(50, nexus_loc):
                    if enemy.is_visible:
                        count_of_visible_enemies += 1

                if count_of_visible_enemies > 0:
                    self.RETURN_TO_BASE = False
                    self.ENEMY_UNITS_VISIBLE = True
                elif count_of_visible_enemies == 0:
                    self.RETURN_TO_BASE = True
                    self.ENEMY_UNITS_VISIBLE = False

            elif self.ATTACK_UNITS > 14:
                if(len(self.known_enemy_units) < 1):
                    self.RETURN_TO_BASE = True
                    self.ENEMY_UNITS_VISIBLE = False
                else:
                    self.RETURN_TO_BASE = False
                    self.ENEMY_UNITS_VISIBLE = True

        if self.ENEMY_UNITS_VISIBLE and len(self.known_enemy_units.closer_than(50, nexus_loc)) > 0:
            for u in self.units.exclude_type(PROBE):
                if len(self.known_enemy_units) > 0:
                    enemy = self.known_enemy_units.closer_than(50, nexus_loc).closest_to(u)
                    if enemy.is_visible:
                        if enemy.is_flying:
                            if u.can_attack_air and u.is_idle:
                                await self.do(u.attack(enemy))
                                self.RETURN_TO_BASE = False
                        else:
                            if u.can_attack_ground and u.is_idle:
                                await self.do(u.attack(enemy))
                                self.RETURN_TO_BASE = False

        elif self.ATTACK_UNITS > 14 and len(self.known_enemy_units) > 0:
            for u in self.units.exclude_type(PROBE):
                enemy = self.known_enemy_units.closest_to(u)
                if enemy.is_flying:
                    if u.can_attack_air and u.is_idle:
                            await self.do(u.attack(enemy))
                            self.RETURN_TO_BASE = False
                else:
                    if u.can_attack_ground and u.is_idle:
                        await self.do(u.attack(enemy))
                        self.RETURN_TO_BASE = False

        elif (self.time - self.MOVE_TIMER) > 5 and self.RETURN_TO_BASE == True:
            if len(self.units(NEXUS).ready) < 3:
                guard_location = self.units(NEXUS).ready
                location = guard_location.center.towards(self.game_info.map_center, randint(10,12))
            else:
                guard_location = self.units(NEXUS).ready.closest_to(self.game_info.map_center)
                location = guard_location.position.towards(self.game_info.map_center, randint(10,12))

            self.MOVE_TIMER = self.time
            for u in self.units.exclude_type(PROBE):
                if u.can_attack_ground or u.can_attack_air and u.is_idle:
                    await self.do(u.move(location))

run_game(maps.get("HonorgroundsLE"), [
    Bot(Race.Protoss, SentdeBot()),
    Computer(Race.Terran, Difficulty.Hard)

], realtime=True)
