"""Execute private projectile constructors; generic allocation/rendering isolated."""
import math,re,struct
from pathlib import Path
from unicorn.mips_const import UC_MIPS_REG_A0, UC_MIPS_REG_A2


def test_weapons(r):
    saved=dict(r.services)
    size,life,vel,parent,owner,damage,radius,charge_owner,mobj,tilt_life,smash_life,tilt_speed,smash_speed,jolt_life,pk_life=struct.unpack('>15I',r.read(r.addr('ccNeutralWeaponLayout'),60))
    g,wp,obj,mat,pos=0x80218000,0x80219000,0x8021A000,0x8021B000,0x8021C000
    def allocation():
        r.write(g,bytes(256));r.write(wp,bytes(size));r.write(obj,bytes(256));r.write(mat,bytes(256))
        r.u32(g+0x84,wp);r.u32(g+r.layout['obj'],obj);r.u32(obj+mobj,mat)
        r.u32(wp+owner,r.GOBJ);r.u32(wp+0x18,r.u32(r.FP+0x44))
        return g
    r.services[0x801655C8]=allocation
    r.services[0x800269C0]=lambda:0
    r.services[0x800E6F24]=lambda:0
    r.services[0x800E02A8]=lambda:0
    lab=Path(__file__).resolve().parents[2]/'ssb-decomp-re'
    source=(lab/'src/wp/wpmain.c').read_text(encoding='utf-8')
    symbols={name:int(address,16) for address,name in re.findall(r'// (0x[0-9A-Fa-f]{8})[^\n]*\n(?:[\w*]+\s+)+(\w+)\(',source)}
    for name in ('wpMainVelSetModelPitch','wpMainVelSetLR','wpMainPlayFGM'):
        r.services[symbols[name]]=lambda:0
    r.call('ccReset');r.setup(0,0);r.preset(0,0,10)
    r.write(pos,struct.pack('>3f',10,20,0))
    for index in (0,1):
        assert r.call('ccwp_wpMarioFireballMakeWeapon',r.GOBJ,pos,index)==g
        assert r.u32(wp+life)==(140 if index==0 else 80)
        expected=(50*math.cos(math.radians(-5)),50*math.sin(math.radians(-5))) if index==0 else (36,0)
        assert max(abs(r.f32(wp+vel+i*4)-v) for i,v in enumerate(expected))<.001
        r.call('ccwp_wpMarioFireballProcUpdate',g)
        assert r.u32(wp+life)==(139 if index==0 else 79)
        assert abs(r.f32(wp+vel+4)-(expected[1]-(1.2 if index==0 else 0)))<.001
    r.write(pos+16,struct.pack('>3f',20,-20,0))
    assert r.call('ccwp_wpPikachuThunderJoltAirMakeWeapon',r.GOBJ,pos,pos+16)==g
    assert r.u32(wp+life)==jolt_life and r.read(wp+vel,12)==r.read(pos+16,12)
    assert r.call('ccwp_wpNessPKFireMakeWeapon',r.GOBJ,pos,pos+16,0)==g
    assert r.u32(wp+life)==pk_life and r.read(wp+vel,12)==r.read(pos+16,12)
    for charge in range(8):
        assert r.call('ccwp_wpSamusChargeShotMakeWeapon',r.GOBJ,pos,charge,1)==g
        assert r.u32(wp+damage)==(3,6,9,12,15,18,21,26)[charge]
        assert r.f32(wp+vel)==(60,62,64,66,68,70,72,74)[charge]
        assert r.f32(wp+radius)==(50,60,70,80,90,100,120,130)[charge]
        assert r.u32(wp+charge_owner)==0
        assert r.call('ccwp_wpSamusChargeShotProcDead',g)==1
    # The constructor consumes our smash flag. A reflected weapon may change
    # native player_num, so lifecycle validity follows the original sidecar.
    r.call('ccNeutral',r.GOBJ)
    state=r.addr('sFTCharBuilderNeutralStates')
    for smash in (0,1):
        r.u32(state+56,smash)
        assert r.call('ccwp_wpLinkBoomerangMakeWeapon',r.GOBJ,pos)==g
        assert r.u32(wp+life)==(smash_life if smash else tilt_life)
        assert abs(r.f32(wp+vel)-(smash_speed if smash else tilt_speed))<.001
        assert r.u32(wp+parent)==r.GOBJ
        r.u32(state+60,g)
        assert r.call('ftMainCharBuilderBoomerangClear',r.FP,g)==1
    # Ending a weapon during another borrowed special must still clear its
    # actual body's sidecar, so the next Neutral B can throw a new one.
    r.u32(state+60,g);r.u32(r.FP+8,7)
    r.u32(r.labels['CharCreator.body_character_data'],r.ATTR)
    r.u32(r.labels['CharCreator.body_character_id'],0)
    r.u32(r.labels['CharCreator.active_special_donor'],7)
    assert r.call('ftMainCharBuilderBoomerangClear',r.FP,g)==1
    assert r.u32(state+60)==0
    r.u32(r.FP+8,0);r.u32(r.labels['CharCreator.body_character_data'],0)
    r.u32(r.labels['CharCreator.active_special_donor'],-1)
    r.u32(state+60,g)
    r.u32(r.FP+r.player_num,r.u32(r.FP+r.player_num)+1)
    assert r.call('ccwp_wpLinkBoomerangProcUpdate',g)==1
    assert r.u32(wp+parent)==0
    for address in list(r.services):
        if address not in saved:del r.services[address]
    r.services.update(saved)
    print('PASS: private Fireball gravity/lifetime, Jolt/PK Fire velocity, all eight Charge Shot sizes/damage/speeds and tilt/smash Boomerang ownership/generation execute on MIPS; allocation/rendering are fixtures.')
