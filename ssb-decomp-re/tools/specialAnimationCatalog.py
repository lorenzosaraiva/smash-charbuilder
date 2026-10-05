"""Visual phases keyed to the existing borrowed-special gameplay definitions."""
from functools import lru_cache
from customAnimation import animation, flag_word
from customMoveCatalog import ROSTER, motion_descriptors
from customMoveTiming import animation_duration
from auditNormalMoves import ROOT, enum_values, us_text

# Only standalone common effects; never execute donor model/texture changes or
# the engine's actor-specific effect constructors through a foreign body.
SAFE_EFFECTS = set('DustLight DustDashSmall DustDashLarge DustHeavyDouble DustHeavyReverse DustExpandLarge DustExpandSmall DamageFlyMDustReverse FlameRandom HealSparkles ImpactWave Psionic QuakeMag0 QuakeMag1 QuakeMag2 Ripple SparkleWhite SparkleWhiteMultiExplode SparkleWhiteScale StarRodSpark ThunderAmp'.split())

def visual_script(events):
    result=[];tick=0
    for op,args in events:
        if op=='ftMotionCommandWait':tick+=int(args[0],0)
        elif op=='ftMotionCommandWaitAsync':tick=max(tick,int(args[0],0))
        elif op=='ftMotionCommandEffect' and args[1].removeprefix('nEFKind') in SAFE_EFFECTS:
            result.extend(('ftMotionCommandWaitAsync('+str(tick)+')',op+'('+','.join(args)+')'))
        elif op=='ftMotionPlayFGM':
            result.extend(('ftMotionCommandWaitAsync('+str(tick)+')',op+'('+','.join(args)+')'))
    return tuple(result)+('ftMotionCommandEnd()',)


@lru_cache(None)
def catalog():
    from generateNeutralActions import catalog as actions
    from generateNeutralProjectiles import catalog as projectiles
    from generateSpecialTiming import path_catalog, special_commands, catalog as timing_catalog
    common = enum_values((ROOT/'src/ft/ftdef.h').read_text(), 'FTCommonMotion')
    result = []

    def add(fighter, name, flags, duration, binding, phase, donor=None, motion=-1, events=None):
        native_duration = animation_duration('&ll'+name+'FileID')
        path, _ = animation(name)
        loop = 'ftAnimLoop(' in us_text(path.read_text())
        # Retain the first cycle and the steady cycle. Gameplay clocks may
        # continue beyond a pose's period (PK Thunder launch/Thunder hit).
        if events is None:
            desc=next(d for d in motion_descriptors(fighter)[1] if d[0]=='&ll'+name+'FileID' and flag_word(d[2])==flags)
            events=special_commands(desc[1]) if desc[1]!='0x80000000' else ()
        result.append(dict(fighter=fighter, name=name, flags=flags, visual=visual_script(events),
                           frames=max(duration, native_duration*(2 if loop else 1))+1,
                           loop_start=native_duration if loop else 0,
                           loop_period=native_duration if loop else 0,
                           binding=binding, phase=phase,
                           donor=ROSTER.index(fighter) if donor is None else donor,
                           motion=motion))

    for air, motion in enumerate(('SpecialN', 'SpecialAirN')):
        ids = enum_values((ROOT/'src/ft/ftchar/ftfox/ftfox.h').read_text().replace('nFTCommonMotionSpecialStart', str(common['nFTCommonMotionSpecialStart'])), 'ftFoxMotion')
        desc = motion_descriptors('Fox')[1][ids['nFTFoxMotion'+motion]]
        add('Fox', desc[0][3:-6], flag_word(desc[2]), animation_duration(desc[0]),
            '&sFTCharBuilderLaserMoves['+str(air)+']', motion)
    for i, c in enumerate(projectiles()):
        add(c['fighter'], c['animation'], c['flags'], c['duration'],
            '&sFTCharBuilderProjectileMoves['+str(i//2)+']['+str(i%2)+']', 'Projectile'+str(c['air']))
    for i, c in enumerate(actions()):
        add(c['fighter'], c['animation'], c['flags'], c['duration'],
            '&sFTCharBuilderActions['+str(i)+'].move', c['phase']+str(c['air']), events=c['events'])
    for i, c in enumerate(path_catalog()):
        add(c['fighter'], c['animation'], c['flags'], c['duration'],
            '&sFTCharBuilderSpecialPaths['+str(i)+'].move', c['phase'], motion=c['motion'], events=c['events'])
    # Hand Slap uses its existing timing-only definitions and separate collision
    # trajectory, rather than the general Up/Down B path registry.
    for i,(donor,motion,duration,cycle,key) in enumerate(timing_catalog()):
        if donor==2 and 'Lw' in key:
            desc=motion_descriptors('Donkey')[1][motion]
            add('Donkey',desc[0][3:-6],flag_word(desc[2]),duration,
                '&sFTCharBuilderSpecialTimings['+str(i)+'].move',key,motion=motion)
    for fighter in ('Mario', 'Luigi', 'Link', 'Samus', 'Fox', 'Pikachu', 'Captain', 'Ness'):
        for phase in ('FallSpecial', 'LandingFallSpecial'):
            desc = motion_descriptors(fighter)[1][common['nFTCommonMotion'+phase]]
            add(fighter, desc[0][3:-6], flag_word(desc[2]), animation_duration(desc[0]),
                None, phase, motion=common['nFTCommonMotion'+phase])
    return tuple(result)
