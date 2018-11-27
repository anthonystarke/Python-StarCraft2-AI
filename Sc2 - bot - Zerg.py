from functools import reduce
from operator import or_
import random

import sc2
from sc2 import run_game, maps, Race, Difficulty, position
from sc2.constants import  LARVA, ZERGLING, HYDRALISK, OVERLORD, HYDRALISKDEN, DRONE, QUEEN, SPAWNINGPOOL, EXTRACTOR, LAIR, EFFECT_INJECTLARVA,HATCHERY, \
ROACH, MUTALISK, HIVE, AbilityId, BuffId, QUEENSPAWNLARVATIMER, RESEARCH_PNEUMATIZEDCARAPACE,RESEARCH_ZERGLINGMETABOLICBOOST, ROACHWARREN, SPIRE, EVOLUTIONCHAMBER, \
RESEARCH_MUSCULARAUGMENTS, RESEARCH_GROOVEDSPINES ,RESEARCH_ZERGMELEEWEAPONSLEVEL1 ,RESEARCH_ZERGMELEEWEAPONSLEVEL2 ,RESEARCH_ZERGMELEEWEAPONSLEVEL3, \
RESEARCH_ZERGMISSILEWEAPONSLEVEL1, RESEARCH_ZERGMISSILEWEAPONSLEVEL2, RESEARCH_ZERGMISSILEWEAPONSLEVEL3, RESEARCH_ZERGGROUNDARMORLEVEL1 , RESEARCH_ZERGGROUNDARMORLEVEL2, \
RESEARCH_ZERGGROUNDARMORLEVEL3, INFESTATIONPIT,RESEARCH_ZERGLINGADRENALGLANDS, MORPH_OVERSEER,OVERSEER

from sc2.player import Bot, Computer
from sc2.data import race_townhalls

from random import randint
import random
import enum

class ZergMaster(sc2.BotAI):
    
    def __init__(self):
        self.MAX_DRONES = 80
        self.ADVANCED_UNITS = False
        self.ATTACKED = False
        self.BUILDING_COUNTER = 0
        self.MOVE_TIMER = 0
        
        self.PENDING_OVERLORD = 0
        self.PENDING_DRONE = 0
        self.PENDING_EXTRACTOR = 0

        self.MACRO_HATCHERY = 0
        self.MAIN_BASE_HATCHERY = 1

        self.SCOUT_TURNING_BACK = False
        self.RETURN_TO_BASE = True
        self.RETURN_TO_BASE_TIMER = 0
        self.ENEMY_UNITS_VISIBLE = False
        self.ENEMY_CLOSE_TO_BASE = False
        self.ATTACK_UNITS = 0
        
        self.FULL_ATTACK = False

        self.COUNT_OF_VISIBLE_ENEMIES = 0
                
        self.PNEUMATIZEDCARAPACE_STARTED = False
        self.ZERGLING_BOOST_STARTED = False
        self.MUSCULARAUGMENTS_STARTED = False
        self.GROOVEDSPINES_STARTED = False
        self.ADRENALGLANDS_STARTED = False
        self.MELEE_UPGRADE = 0
        self.MISSILE_UPGRADE = 0
        self.ARMOR_UPGRADE = 0

        self.AIR_WEAPONS_UPGRADE = 0
        self.AIR_ARMOR_UPGRADE = 0
        print(dir(sc2.constants))

    def select_target(self):
        if self.known_enemy_structures.exists:
            return random.choice(self.known_enemy_structures).position

        return self.enemy_start_locations[0]

    async def on_step(self, iteration):
        
        await self.scouting()
        await self.distribute_workers()
        await self.build_workers() 
       
        #Test
        await self.build_attack_force()
        
        await self.build_supply()
        await self.build_extractor()
        
        await self.build_support_mobs()
        await self.support_mobs_ability()
        
        await self.build_buildings()
        # await self.pre_expand()
        
        await self.expand()

        await self.upgrades()
                
        self.Attack_units_counter()
        
        await self.upgrade_overlords()

        if self.ATTACK_UNITS > 0:
            # await self.attack()
            await self.attack_v2()

    async def upgrade_overlords(self):

        if(len(self.units(OVERLORD).ready) > 5 and self.units(LAIR).exists and self.ATTACK_UNITS > 20):
            overlords = self.units(OVERLORD).ready.idle
            for overlord in overlords:
                abilities = await self.get_available_abilities(overlord)
                if AbilityId.MORPH_OVERSEER in abilities:
                    await self.do(overlord(MORPH_OVERSEER))
                    continue

    async def scouting(self):
        
        if len(self.known_enemy_structures) < 3:
            self.SCOUT_TURNING_BACK = False
            if len(self.units(OVERLORD).ready.idle) > 2:
                s = self.units(OVERLORD).ready.idle
                # scout = self.units(OVERLORD).ready
                enemy_location = self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)]
                move_to = self.random_location_variance(enemy_location)
                await self.do(s[0].move(move_to))
                
                enemy_location = self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)]
                move_to = self.random_location_variance(enemy_location)
                await self.do(s[1].move(move_to))
                
                enemy_location = self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)]
                move_to = self.random_location_variance(enemy_location)
                await self.do(s[2].move(move_to))
            else:
                if len(self.units(OVERLORD).ready.idle) > 0:
                    s = self.units(OVERLORD).ready.idle
                    enemy_location = self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)]
                    move_to = self.random_location_variance(enemy_location)
                    await self.do(s[0].move(move_to))
        else:
            if len(self.units(OVERLORD).ready) < 2 and self.SCOUT_TURNING_BACK == False:
                s = self.units(OVERLORD).ready
                guard_location = self.townhalls.ready
                location = guard_location.center.towards(self.game_info.map_center, randint(10,12))
                await self.do(s.move(location))
                self.SCOUT_TURNING_BACK = True

            elif len(self.units(OVERLORD).ready) > 2 and self.SCOUT_TURNING_BACK == False:
                s = self.units(OVERLORD).ready
                guard_location = self.townhalls.ready
                location = guard_location.center.towards(self.game_info.map_center, randint(10,12))
                await self.do(s[0].move(location))
                await self.do(s[1].move(location))
                await self.do(s[2].move(location))
                self.SCOUT_TURNING_BACK = True
            

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
        
        if not self.already_pending(DRONE):
            self.PENDING_DRONE = 0

        larvae = self.units(LARVA)
        
        if len(self.townhalls.ready) > 2:
            if len(self.units(DRONE).ready) < len(self.townhalls) * 22 and len(self.units(DRONE).ready) < self.MAX_DRONES:
                if self.PENDING_DRONE < 3:
                    if self.can_afford(DRONE) and larvae.exists:
                        larva = larvae.random
                        self.PENDING_DRONE += 1
                        await self.do(larva.train(DRONE))
                        return
        else:
            if len(self.units(DRONE).ready) < len(self.townhalls) * 22 and len(self.units(DRONE).ready) < self.MAX_DRONES:
                if self.can_afford(DRONE) and larvae.exists:
                    if self.PENDING_DRONE < 4:
                        larva = larvae.random
                        self.PENDING_DRONE += 1
                        await self.do(larva.train(DRONE))
                        return

    async def build_supply(self):
        
        if not self.already_pending(OVERLORD):
            self.PENDING_OVERLORD = 0

        larvae = self.units(LARVA)
        
        if len(self.townhalls.ready) > 1:
            if self.supply_left < 20 and self.supply_cap < 200:
                if self.can_afford(OVERLORD) and larvae.exists: # and self.PENDING_OVERLORD < 4:
                    larva = larvae.random
                    self.PENDING_OVERLORD += 1
                    await self.do(larva.train(OVERLORD))
        elif len(self.townhalls.ready) == 1:
            if self.supply_left < 20 and self.supply_cap < 200:
                if self.can_afford(OVERLORD) and larvae.exists and self.PENDING_OVERLORD < 2:
                    larva = larvae.random
                    self.PENDING_OVERLORD += 1
                    await self.do(larva.train(OVERLORD))

    async def build_extractor(self):
        
        if not self.already_pending(EXTRACTOR):
            self.PENDING_EXTRACTOR = 0
        
        for hq in self.townhalls.ready:
            vaspenes = self.state.vespene_geyser.closer_than(10,hq)
            for vaspene in vaspenes:
                if self.can_afford(EXTRACTOR): #and self.PENDING_EXTRACTOR < 2:
                    worker = self.select_build_worker(vaspene.position)
                    if worker is None:
                        break
                    if not self.units(EXTRACTOR).closer_than(1.0, vaspene).exists:
                        await self.do(worker.build(EXTRACTOR, vaspene))
                        self.PENDING_EXTRACTOR += 1

    async def build_support_mobs(self):
        for hq in self.townhalls.ready:
            if self.units(SPAWNINGPOOL).ready.exists:
                if (len(self.units(QUEEN).ready) < len(self.townhalls.ready)) and (len(self.units(QUEEN).ready) < 6) and hq.is_ready and hq.noqueue:
                    if self.can_afford(QUEEN):
                        await self.do(hq.train(QUEEN))

    async def support_mobs_ability(self):
        hq = self.townhalls.ready
        applying_buff = [False] * len(self.townhalls.ready)
        for queen in self.units(QUEEN).ready.idle:    
        
            for i in range(len(self.townhalls.ready)):

                if hq[i].has_buff(QUEENSPAWNLARVATIMER) or applying_buff[i] == True:
                    continue
                
                abilities = await self.get_available_abilities(queen)
                if AbilityId.EFFECT_INJECTLARVA in abilities:
                    applying_buff[i] = True
                    await self.do(queen(EFFECT_INJECTLARVA, hq[i]))
                    continue
            
    async def build_buildings(self):
        location = self.townhalls.first.position.towards(self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)], random.randrange(2, 4))
        
        if not self.units(SPAWNINGPOOL).exists and not self.already_pending(SPAWNINGPOOL):
            if self.can_afford(SPAWNINGPOOL):
                await self.build(SPAWNINGPOOL, near=location)
        
        if self.units(SPAWNINGPOOL).ready.exists and not self.units(ROACHWARREN).exists and not self.already_pending(ROACHWARREN) and len(self.townhalls.ready) > 1:
            if self.can_afford(ROACHWARREN):
                await self.build(ROACHWARREN, near=location)

        if not self.units(HYDRALISKDEN).exists and not self.already_pending(HYDRALISKDEN) and self.units(LAIR).exists:
            if self.can_afford(HYDRALISKDEN):
                await self.build(HYDRALISKDEN, near=location)

        if not self.units(SPIRE).exists and not self.already_pending(SPIRE) and self.units(LAIR).exists:
            if self.can_afford(SPIRE):
                await self.build(SPIRE, near=location)

        if not self.units(EVOLUTIONCHAMBER).exists and not self.already_pending(EVOLUTIONCHAMBER) and self.units(SPAWNINGPOOL).ready.exists and len(self.townhalls.ready) > 2:
            if self.can_afford(EVOLUTIONCHAMBER):
                await self.build(EVOLUTIONCHAMBER, near=location)

        if not self.units(INFESTATIONPIT).exists and not self.already_pending(INFESTATIONPIT) and self.units(LAIR).ready.exists and len(self.townhalls.ready) > 3:
            if self.can_afford(INFESTATIONPIT):
                await self.build(INFESTATIONPIT, near=location)

    async def pre_expand(self):
        if len(self.townhalls.ready) > 2:
            if self.MACRO_HATCHERY < self.MAIN_BASE_HATCHERY:
                for hq in self.townhalls:
                    if not self.already_pending(HATCHERY):
                        location = hq.position.towards(self.enemy_start_locations[randint(0,len(self.enemy_start_locations)-1)], random.randrange(5, 10))
                        if self.can_afford(HATCHERY):
                            self.MACRO_HATCHERY += 1
                            await self.build(HATCHERY, near=location)

    async def expand(self):
        # if self.MACRO_HATCHERY == self.MAIN_BASE_HATCHERY: 
        if len(self.townhalls.ready) > 2:
            if len(self.townhalls) < 10 and self.can_afford(HATCHERY) and self.ATTACK_UNITS > 35:
                self.MAIN_BASE_HATCHERY += 1
                await self.expand_now()
                    
        elif len(self.townhalls.ready) < 3 and (len(self.units(SPAWNINGPOOL)) > 0 or self.already_pending(SPAWNINGPOOL)) and (self.ATTACK_UNITS > 5 or self.minerals > 600):
            if self.can_afford(HATCHERY):
                self.MAIN_BASE_HATCHERY += 1
                await self.expand_now()

    async def upgrades(self):

        if self.units(SPAWNINGPOOL).ready:
            sp = self.units(SPAWNINGPOOL).ready
            if sp.noqueue:
                if self.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST) and self.ZERGLING_BOOST_STARTED == False:
                    self.ZERGLING_BOOST_STARTED = True
                    await self.do(sp.first(RESEARCH_ZERGLINGMETABOLICBOOST))
                
                if self.can_afford(RESEARCH_ZERGLINGADRENALGLANDS) and self.units(HIVE).ready and self.ADRENALGLANDS_STARTED == False:
                    self.ADRENALGLANDS_STARTED = True
                    await self.do(sp.first(RESEARCH_ZERGLINGADRENALGLANDS))
        

        if len(self.townhalls) > 2:
            for hq in self.townhalls:
                if not self.units(LAIR).exists and hq.noqueue:
                    if self.can_afford(LAIR):
                        await self.do(hq.build(LAIR))
                        
                if not self.units(HIVE).exists and hq.noqueue:
                    if self.can_afford(HIVE):
                        await self.do(hq.build(HIVE))

                elif self.can_afford(RESEARCH_PNEUMATIZEDCARAPACE) and self.PNEUMATIZEDCARAPACE_STARTED == False :
                    self.PNEUMATIZEDCARAPACE_STARTED = True
                    await self.do(hq(RESEARCH_PNEUMATIZEDCARAPACE))

        if self.units(HYDRALISKDEN).ready:
            hd = self.units(HYDRALISKDEN).ready
            if hd.noqueue:
                if self.can_afford(RESEARCH_MUSCULARAUGMENTS) and self.MUSCULARAUGMENTS_STARTED == False:
                    self.MUSCULARAUGMENTS_STARTED = True
                    await self.do(hd.first(RESEARCH_MUSCULARAUGMENTS))
            
                if self.can_afford(RESEARCH_GROOVEDSPINES) and self.GROOVEDSPINES_STARTED == False:
                    self.GROOVEDSPINES_STARTED = True
                    await self.do(hd.first(RESEARCH_GROOVEDSPINES))

        if self.units(EVOLUTIONCHAMBER).ready and len(self.townhalls.ready) > 2:
            ec = self.units(EVOLUTIONCHAMBER).ready.noqueue
            if ec.noqueue:
                if self.can_afford(RESEARCH_ZERGMELEEWEAPONSLEVEL1) and self.MELEE_UPGRADE == 0:
                    await self.do(ec.first(RESEARCH_ZERGMELEEWEAPONSLEVEL1))
                    self.MELEE_UPGRADE = 1
                elif self.can_afford(RESEARCH_ZERGMELEEWEAPONSLEVEL2) and self.MELEE_UPGRADE == 1 and self.units(LAIR).ready  :
                    await self.do(ec.first(RESEARCH_ZERGMELEEWEAPONSLEVEL2))
                    self.MELEE_UPGRADE == 2
                elif self.can_afford(RESEARCH_ZERGMELEEWEAPONSLEVEL3) and self.MELEE_UPGRADE == 2 and self.units(HIVE).ready  :
                    await self.do(ec.first(RESEARCH_ZERGMELEEWEAPONSLEVEL3))
                    self.MELEE_UPGRADE == 3

                if self.can_afford(RESEARCH_ZERGMISSILEWEAPONSLEVEL1) and self.MISSILE_UPGRADE == 0:
                    await self.do(ec.first(RESEARCH_ZERGMISSILEWEAPONSLEVEL1))
                    self.MISSILE_UPGRADE = 1
                elif self.can_afford(RESEARCH_ZERGMISSILEWEAPONSLEVEL2) and self.MISSILE_UPGRADE == 1 and self.units(LAIR).ready  :
                    await self.do(ec.first(RESEARCH_ZERGMISSILEWEAPONSLEVEL2))
                    self.MISSILE_UPGRADE == 2
                elif self.can_afford(RESEARCH_ZERGMISSILEWEAPONSLEVEL2) and self.MISSILE_UPGRADE == 2 and self.units(HIVE).ready  :
                    await self.do(ec.first(RESEARCH_ZERGMISSILEWEAPONSLEVEL2))
                    self.MISSILE_UPGRADE == 3

                if self.can_afford(RESEARCH_ZERGGROUNDARMORLEVEL1) and self.ARMOR_UPGRADE == 0:
                    await self.do(ec.first(RESEARCH_ZERGGROUNDARMORLEVEL1))
                    self.ARMOR_UPGRADE = 1
                elif self.can_afford(RESEARCH_ZERGGROUNDARMORLEVEL2) and self.ARMOR_UPGRADE == 1 and self.units(LAIR).ready  :
                    await self.do(ec.first(RESEARCH_ZERGGROUNDARMORLEVEL2))
                    self.ARMOR_UPGRADE == 2
                elif self.can_afford(RESEARCH_ZERGGROUNDARMORLEVEL3) and self.ARMOR_UPGRADE == 2 and self.units(HIVE).ready  :
                    await self.do(ec.first(RESEARCH_ZERGGROUNDARMORLEVEL3))
                    self.ARMOR_UPGRADE == 3

    async def build_attack_force(self):
        larvae = self.units(LARVA).ready

        for larva in larvae:
            
            if self.ATTACK_UNITS < 20 and len(self.townhalls) < 3:

                if self.units(ROACHWARREN).ready.exists and (len(self.townhalls.ready) == 1 or self.already_pending(HATCHERY))and len(self.units(ROACH).ready) < 30:
                            if self.can_afford(ROACH) and larvae.exists and self.supply_left > 2:
                                await self.do(larva.train(ROACH))
                                continue              
                
                if self.units(SPAWNINGPOOL).ready.exists and len(self.townhalls.ready) == 1: 
                    if self.units(SPAWNINGPOOL).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY)) and len(self.units(ZERGLING).ready) < 30:
                            if self.can_afford(ZERGLING) and larvae.exists and self.supply_left > 0:
                                await self.do(larva.train(ZERGLING))
                                continue
                
                elif len(self.townhalls.ready) > 1 and self.units(SPAWNINGPOOL).ready.exists:
                
                        if self.units(SPIRE).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY)):
                            if self.can_afford(MUTALISK) and larvae.exists and self.supply_left > 2:
                                await self.do(larva.train(MUTALISK))
                                continue                        

                        if self.units(HYDRALISKDEN).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY))and len(self.units(HYDRALISK).ready) < 30:
                            if self.can_afford(HYDRALISK) and larvae.exists and self.supply_left > 2:
                                await self.do(larva.train(HYDRALISK))
                                continue                        

                        if self.units(ROACHWARREN).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY))and len(self.units(ROACH).ready) < 30:
                            if self.can_afford(ROACH) and larvae.exists and self.supply_left > 2:
                                await self.do(larva.train(ROACH))
                                continue    

                        if self.units(SPAWNINGPOOL).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY)) and len(self.units(ZERGLING).ready) < 30:
                            if self.can_afford(ZERGLING) and larvae.exists and self.supply_left > 0:
                                await self.do(larva.train(ZERGLING))
                                continue
            
            elif len(self.townhalls) > 2:

                if self.units(ROACHWARREN).ready.exists and (len(self.townhalls.ready) == 1 or self.already_pending(HATCHERY))and len(self.units(ROACH).ready) < 30:
                            if self.can_afford(ROACH) and larvae.exists and self.supply_left > 2:
                                await self.do(larva.train(ROACH))
                                continue              
                
                if self.units(SPAWNINGPOOL).ready.exists and len(self.townhalls.ready) == 1: 
                    if self.units(SPAWNINGPOOL).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY)) and len(self.units(ZERGLING).ready) < 30:
                            if self.can_afford(ZERGLING) and larvae.exists and self.supply_left > 0:
                                await self.do(larva.train(ZERGLING))
                                continue
                
                elif len(self.townhalls.ready) > 1 and self.units(SPAWNINGPOOL).ready.exists:
                
                        if self.units(SPIRE).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY)):
                            if self.can_afford(MUTALISK) and larvae.exists and self.supply_left > 2:
                                await self.do(larva.train(MUTALISK))
                                continue                        

                        if self.units(HYDRALISKDEN).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY))and len(self.units(HYDRALISK).ready) < 30:
                            if self.can_afford(HYDRALISK) and larvae.exists and self.supply_left > 2:
                                await self.do(larva.train(HYDRALISK))
                                continue                        

                        if self.units(ROACHWARREN).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY))and len(self.units(ROACH).ready) < 30:
                            if self.can_afford(ROACH) and larvae.exists and self.supply_left > 2:
                                await self.do(larva.train(ROACH))
                                continue    

                        if self.units(SPAWNINGPOOL).ready.exists and (len(self.townhalls.ready) > 1 or self.already_pending(HATCHERY)) and len(self.units(ZERGLING).ready) < 30:
                            if self.can_afford(ZERGLING) and larvae.exists and self.supply_left > 0:
                                await self.do(larva.train(ZERGLING))
                                continue


    def Attack_units_counter(self):
            self.ATTACK_UNITS = (len(self.units(ZERGLING))/2) + len(self.units(HYDRALISK)) + len(self.units(ROACH)) + len(self.units(MUTALISK))
    
    async def attack_v2(self):
        
        if self.ATTACK_UNITS < 20 and self.FULL_ATTACK == True:
            self.FULL_ATTACK = False
        
        forces = self.units(ZERGLING) | self.units(HYDRALISK) | self.units(MUTALISK) | self.units(ROACH) | self.units(OVERSEER)
        
        if len(self.known_enemy_units) > 0 and self.ATTACK_UNITS > 50 and len(self.townhalls) > 3 or self.supply_cap > 190:
            
            self.FULL_ATTACK = True
            hq = self.townhalls.ready
            
            for unit in forces:
            
                if len(self.known_enemy_units.closer_than(60,hq.center)) > 0:
                    enemy = self.known_enemy_units.closer_than(60,hq.center).closest_to(unit)
                else:
                    enemy = self.known_enemy_units.closest_to(unit)

                # enemy = self.known_enemy_units.closest_to(unit)
                await self.do(unit.attack(enemy.position.towards(self.game_info.map_center, random.randrange(1, 2))))
        
        elif len(self.known_enemy_units) > 0 and self.FULL_ATTACK == False: #and self.ATTACK_UNITS < 39
            
            hq = self.townhalls.ready

            for unit in forces:
                
                if len(self.known_enemy_units.closer_than(50,hq.center)) > 0:
                    enemy = self.known_enemy_units.closer_than(50,hq.center).closest_to(unit)
                
                    if enemy.is_visible:
                        await self.do(unit.attack(enemy.position.towards(self.game_info.map_center, random.randrange(1, 2))))
                else:
                    if len(self.townhalls) < 3:
                        guard_location = self.townhalls
                        location = guard_location.center.towards(self.game_info.map_center, randint(10,12))
                    else:
                        guard_location = self.townhalls.closest_to(self.game_info.map_center)
                        location = guard_location.position.towards(self.game_info.map_center, randint(10,12))

                    await self.do(unit.move(location))
        
        elif len(self.known_enemy_units) == 0 and (self.time - self.RETURN_TO_BASE_TIMER) > 5:
            
            self.RETURN_TO_BASE_TIMER = self.time
            
            self.FULL_ATTACK = False

            if len(self.townhalls.ready) < 3:
                guard_location = self.townhalls
                location = guard_location.center.towards(self.game_info.map_center, randint(10,12))
            else:
                guard_location = self.townhalls.closest_to(self.game_info.map_center)
                location = guard_location.position.towards(self.game_info.map_center, randint(10,12))

            for unit in forces:
                if unit.is_idle:
                    await self.do(unit.move(location))

        # larvae = self.units(LARVA)
        # forces = self.units(ZERGLING) | self.units(HYDRALISK)

        # if self.units(HYDRALISK).amount > 10 and iteration % 50 == 0:
        #     for unit in forces.idle:
        #         await self.do(unit.attack(self.select_target()))

        # if self.supply_left < 2:
        #     if self.can_afford(OVERLORD) and larvae.exists:
        #         await self.do(larvae.random.train(OVERLORD))
        #         return

        # if self.units(HYDRALISKDEN).ready.exists:
        #     if self.can_afford(HYDRALISK) and larvae.exists:
        #         await self.do(larvae.random.train(HYDRALISK))
        #         return

        # if not self.townhalls.exists:
        #     for unit in self.units(DRONE) | self.units(QUEEN) | forces:
        #         await self.do(unit.attack(self.enemy_start_locations[0]))
        #     return
        # else:
        #     hq = self.townhalls.first

        # for queen in self.units(QUEEN).idle:
        #     abilities = await self.get_available_abilities(queen)
        #     if AbilityId.EFFECT_INJECTLARVA in abilities:
        #         await self.do(queen(EFFECT_INJECTLARVA, hq))

        # if not (self.units(SPAWNINGPOOL).exists or self.already_pending(SPAWNINGPOOL)):
        #     if self.can_afford(SPAWNINGPOOL):
        #         await self.build(SPAWNINGPOOL, near=hq)

        # if self.units(SPAWNINGPOOL).ready.exists:
        #     if not self.units(LAIR).exists and hq.noqueue:
        #         if self.can_afford(LAIR):
        #             await self.do(hq.build(LAIR))

        # if self.units(LAIR).ready.exists:
        #     if not (self.units(HYDRALISKDEN).exists or self.already_pending(HYDRALISKDEN)):
        #         if self.can_afford(HYDRALISKDEN):
        #             await self.build(HYDRALISKDEN, near=hq)

        # if self.units(EXTRACTOR).amount < 2 and not self.already_pending(EXTRACTOR):
        #     if self.can_afford(EXTRACTOR):
        #         drone = self.workers.random
        #         target = self.state.vespene_geyser.closest_to(drone.position)
        #         await self.do(drone.build(EXTRACTOR, target))

        # if hq.assigned_harvesters < hq.ideal_harvesters:
        #     if self.can_afford(DRONE) and larvae.exists:
        #         larva = larvae.random
        #         await self.do(larva.train(DRONE))
        #         return

        # for a in self.units(EXTRACTOR):
        #     if a.assigned_harvesters < a.ideal_harvesters:
        #         w = self.workers.closer_than(20, a)
        #         if w.exists:
        #             await self.do(w.random.gather(a))

        # if self.units(SPAWNINGPOOL).ready.exists:
        #     if not self.units(QUEEN).exists and hq.is_ready and hq.noqueue:
        #         if self.can_afford(QUEEN):
        #             await self.do(hq.train(QUEEN))

        # if self.units(ZERGLING).amount < 20 and self.minerals > 1000:
        #     if larvae.exists and self.can_afford(ZERGLING):
        #         await self.do(larvae.random.train(ZERGLING))

def main():
    # HonorgroundsLE
    # AbandonedParish-Revisit
    sc2.run_game(maps.get("HonorgroundsLE"), [
        Bot(Race.Zerg, ZergMaster()),
        Computer(Race.Protoss, Difficulty.Hard),
        Computer(Race.Protoss, Difficulty.Medium),
        Computer(Race.Protoss, Difficulty.Medium)
    ], realtime=True, save_replay_as="ZvT.SC2Replay")

if __name__ == '__main__':
    main()