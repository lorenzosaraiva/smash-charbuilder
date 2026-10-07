"""Real-input special contacts/transitions with explicit positioning fixtures.

No successful status, hit, damage or release outcome is injected. Native code
owns the result; actors/projectiles are positioned for repeatable contacts,
and absorption uses an explicit initial 80-percent fixture.
"""
import hashlib
import json
import math


def run(e):
    args=e['args']; mode=args.edge
    u32,f32,w32,wf32=[e[n] for n in ('u32','f32','w32','wf32')]
    fighter,frames,pulse,wait=[e[n] for n in ('fighter','frames','pulse','wait')]
    keys=e['keys'];layout=e['layout'];ex=e['edge_layout'];labels=e['labels']
    root=lambda p=0:u32(fighter(p)+0x8E8)+layout[12]
    gobj=lambda p=0:u32(fighter(p)+e['normal_fields'][16])
    rows=[];seen=set();reflected=False;contact=False
    initial_damage=80
    stage=e['edge_stage'];map_masks=[];floor_angles=[];fixture=None
    def u16(a):return e['u8'](a)*256+e['u8'](a+1)
    def s16(a):
        v=u16(a);return v-65536 if v&32768 else v
    def segments():
        n=e['native'];info=u32(n['gMPCollisionVertexInfo']);links=u32(n['gMPCollisionVertexLinks'])
        ids=u32(n['gMPCollisionVertexIDs']);data=u32(n['gMPCollisionVertexData']);objects=u32(n['gMPCollisionYakumonoDObjs'])
        for line in range(u32(n['gMPCollisionLinesNum'])):
            vi=info+line*stage[0];obj=u32(objects+e['u8'](vi)*4)
            offset=(f32(obj+layout[12]),f32(obj+layout[12]+4)) if u32(obj+stage[2]) or u32(obj+stage[3]) else (0,0)
            first,count=u16(links+line*4),u16(links+line*4+2)
            points=[]
            for j in range(count):
                v=data+u16(ids+(first+j)*2)*stage[1]
                points.append((s16(v)+offset[0],s16(v+2)+offset[1]))
            for a,b in zip(points,points[1:]):yield line,e['u8'](vi+1),a,b
    keys_port=e['plugins'][1].LabKeysPort
    w32(fighter(1)+layout[1],0)
    w32(fighter(1)+ex[18],u32(fighter()+ex[18])+ex[19])
    keys_port(1,0);frames(5)

    def place(p,point):
        fp=fighter(p)
        for j,v in zip((0,4,8),point):
            wf32(root(p)+j,v);wf32(fp+e['collision_off']+ex[6]+j,v)
            wf32(fp+e['special'][1]+j,0)
        wf32(fp+e['special'][2],0)
        if p==1:
            # The dummy may have started on an upper platform. Use the same
            # native floor as the attacker instead of snapping to its old one.
            w32(fp+e['collision_off']+ex[20],u32(fighter()+e['collision_off']+ex[20]))

    def weapons(kind=None):
        node=u32(e['native']['gGCCommonLinks']+20)
        for _ in range(128):
            if not 0x80000000<=node<0x80800000:break
            wp=u32(node+0x84)
            if 0x80000000<=wp<0x80800000 and (kind is None or u32(wp+ex[0])==kind):yield node,wp
            node=u32(node+4)

    def tick():
        nonlocal reflected,contact
        fp=fighter();status=u32(fp+0x24)
        clock=labels['CharLabRuntime.sCCSpecialClocks']
        move_clock=labels['CharLabRuntime.sFTCustomMoveClocks']
        frame=int(f32(clock+20)) if u32(clock)==fp else int(f32(move_clock+24)) if u32(move_clock)==fp else int(f32(gobj()+0x78))
        mask=sum(1<<i for i in range(4) if u32(fp+e['attack_off']+i*e['attack_size']))
        rows.append((status,frame,mask,u32(fighter(1)+0x24),u32(fighter(1)+e['percent_off']),u32(fp+ex[7])))
        seen.add(status)
        coll=fp+e['collision_off']
        map_masks.append(u16(coll+stage[4])|u16(coll+stage[5]))
        floor_angles.append((f32(coll+stage[7]),f32(coll+stage[7]+4)))
        if mode in ('reflect','absorb'):
            for node,wp in weapons():
                if u32(wp+ex[2])==gobj() or u32(wp+ex[1])==gobj():reflected=True
                if u32(wp+ex[1])==gobj(1):
                    point=u32(node+layout[10])+layout[12]
                    for j in (0,4,8):wf32(point+j,f32(root()+j)+(200 if j==4 else 0))
                    contact=True
        if mode=='thunder-contact' and not contact:
            for node,wp in weapons(11):
                point=u32(node+layout[10])+layout[12]
                for j in (0,4,8):wf32(point+j,f32(root()+j)+(225 if j==4 else 0))
                contact=True;break
        if mode=='sing' and mask:
            center=fp+e['attack_off']+e['center_off']
            place(1,(f32(center),f32(root()+4),f32(center+8)));contact=True

    e['edge_tick']=tick;e['tracking']=True
    checks=[]
    if mode=='quick-ledge':
        n=e['native'];links=u32(n['gMPCollisionVertexLinks']);ids=u32(n['gMPCollisionVertexIDs']);data=u32(n['gMPCollisionVertexData'])
        candidates=[]
        for line,kind,a,b in segments():
            first,count=u16(links+line*4),u16(links+line*4+2)
            if kind==0 and any(u16(data+u16(ids+(first+j)*2)*stage[1]+4)&stage[12] for j in range(count)):
                candidates.extend((line,point) for point in (a,b))
        assert candidates,('No native ledge geometry',args.stage,list(segments()))
        fixture=min(candidates,key=lambda c:c[1][0]);line,(x,y)=fixture
        pulse(0x800);frames(6);pulse(0x40|(80<<24))
        place(0,(x-350,y-200,0));keys(80<<16);frames(40);keys(0)
        assert seen.intersection(stage[10:12]),('Quick Attack did not catch native ledge',fixture,seen,map_masks)
        frames(5);pulse(0x80);frames(90)
        checks=['stage-derived ledge positioning','real Quick Attack input','native ledge catch','real ledge attack input and recovery']
    elif mode in ('quick-wall','slope'):
        if mode=='quick-wall':
            candidates=[s for s in segments() if s[1] in (2,3) and abs(s[3][1]-s[2][1])>600 and min(s[2][1],s[3][1])>=0]
        else:
            candidates=[s for s in segments() if s[1]==0 and abs(s[3][1]-s[2][1])>40 and abs(s[3][0]-s[2][0])>400]
        assert candidates,('No suitable stage geometry',args.stage,list(segments()))
        fixture=max(candidates,key=lambda s:abs(s[3][1]-s[2][1]) if mode=='quick-wall' else abs(s[3][0]-s[2][0]))
        line,kind,a,b=fixture;x=(a[0]+b[0])/2;y=(a[1]+b[1])/2
        pulse(0x800);frames(6)
        if mode=='quick-wall':
            direction=-1 if kind==2 else 1
            place(0,(x-direction*450,y-f32(fighter()+e['collision_off']+stage[6]),0))
            pulse(0x40|(80<<24));keys((80 if direction>0 else 176)<<16)
            def wall_endpoint():
                coll=fighter()+e['collision_off']
                if u32(fighter()+0x24)==e['special'][7] and (u16(coll+stage[4])|u16(coll+stage[5]))&stage[8]:
                    seen.add(e['special'][7]);return True
                return False
            wait(wall_endpoint,'Quick Attack native wall endpoint')
            # Recover toward the stage after the wall ends the horizontal zip.
            keys((176<<16)|(80<<24));frames(12);keys(176<<16);frames(100);keys(0)
            assert not seen.intersection((0,7,8,9)),('Wall test KO',fixture,seen)
            checks=['stage-derived wall positioning','real Quick Attack input','native wall collision/end transition']
        else:
            place(0,(x,y+200,0));wait(lambda:u32(fighter()+0x24)==10,'Natural landing on slope')
            pulse(0x40|(176<<24));frames(180)
            assert any(abs(v[0])>.01 for v in floor_angles),('Native slope normal absent',fixture)
            assert any(r[0]>=220 for r in rows),('Slope special never entered',seen)
            assert not seen.intersection((0,7,8,9)),('Slope test KO',fixture,seen)
            checks=['stage-derived slope positioning','native slope floor normal','real Falcon Kick input and recovery']
    elif mode=='grounded-only':
        pulse(0x800);frames(5);pulse(0x40|(176<<24));frames(75)
        assert rows and not any(r[0]>=220 for r in rows),('Ground-only donor fell back to body',rows)
        wait(lambda:u32(fighter()+0x24)==10,'Landing after unavailable donor')
        pulse(0x40|(176<<24));frames(160)
        assert ex[15] in seen,('Grounded DK move lost after rejection',seen)
        checks=['airborne Down B rejected without body fallback','configured grounded move still works']
    elif mode in ('dk-single','dk-repeat'):
        place(1,(f32(root())+150,f32(root()+4),f32(root()+8)))
        pulse(0x40|(176<<24));wait(lambda:u32(fighter()+0x24)==ex[15],'DK slap loop')
        frames(5)
        if mode=='dk-repeat':pulse(0x40)
        frames(170)
        # Hitlag repeats the same source frame while the native clock is paused.
        distinct=[r for i,r in enumerate(rows) if i==0 or r[:3]!=rows[i-1][:3]]
        active=[r[1] for r in distinct if r[0]==ex[15] and r[2]]
        assert active==[16,17,26,27]*(2 if mode=='dk-repeat' else 1),('Donor slap windows',active)
        assert max(r[4] for r in rows)>0, 'Repeated DK attacks never contacted opponent'
        checks=['two native DK cycles' if mode=='dk-repeat' else 'single tap produces one DK cycle','original slap hit windows including hitlag','native opponent contact/damage']
    elif mode=='ness-launch':
        place(1,(f32(root())+1800,f32(root()+4),f32(root()+8)))
        pulse(0x40|(80<<24));wait(lambda:u32(fighter()+0x24) in ex[9:11],'PK Thunder hold')
        head=lambda:next(weapons(14),None)
        wait(lambda:head() is not None,'Native PK Thunder head')
        keys(80<<16);frames(8);right=tuple(f32(head()[1]+ex[4]+j) for j in (0,4,8))
        keys(176<<16);frames(8);left=tuple(f32(head()[1]+ex[4]+j) for j in (0,4,8));keys(0)
        assert math.dist(right,left)>1,('PK Thunder steering absent',right,left)
        wait(lambda:u32(fighter()+ex[5])==0,'PK Thunder self-contact delay')
        e['check'](e['core'].CoreDoCommand(7,0,None));wait(e['paused'],'Pause for PK Thunder positioning')
        node,wp=head();point=u32(node+layout[10])+layout[12]
        wf32(point,f32(root()));wf32(point+4,f32(root()+4)+50);wf32(point+8,0)
        e['check'](e['core'].CoreDoCommand(8,0,None))
        wait(lambda:u32(fighter()+0x24) in ex[11:13],'Native PK Thunder self-launch')
        frames(240)
        assert seen.intersection(ex[11:13]),('PK Thunder self-launch missing',seen)
        assert not seen.intersection((0,7,8,9)),('PK Thunder recovery fixture reached a KO',seen)
        checks=['real PK Thunder steering','controlled native self-contact','launch, movement and recovery']
    elif mode=='thunder-contact':
        pulse(0x40|(176<<24));frames(240)
        assert contact and seen.intersection(ex[13:15]),('Thunder owner hit phase missing',seen)
        checks=['native Thunder creation','controlled owner contact','hit/end/recovery and pointer cleanup']
    elif mode in ('reflect','absorb'):
        if mode=='absorb':w32(fighter()+e['percent_off'],initial_damage)
        keys(0x40|(176<<24));frames(18)
        offset,mask=e['edge_bits'][mode]
        wait(lambda:e['u8'](fighter()+offset)&mask,'Donor special collision flag')
        keys_port(1,0x40);frames(3);keys_port(1,0);frames(65)
        assert contact, ('Enemy Fireball input/weapon missing',mode)
        if mode=='reflect':assert reflected,('Native projectile reflection missing',seen)
        else:assert u32(fighter()+e['percent_off'])<initial_damage,('Native PSI healing missing',u32(fighter()+e['percent_off']))
        keys(0);frames(90)
        assert not e['u8'](fighter()+offset)&mask,('Special collision survived recovery',mode)
        checks=['real opponent Fireball input','controlled projectile contact','native '+mode+' outcome','volume cleanup']
    elif mode in ('sing','rest'):
        place(1,(f32(root())+80,f32(root()+4),f32(root()+8)))
        pulse(0x40|((176 if mode=='rest' else 80)<<24));frames(330)
        if mode=='sing':assert contact and any(r[3]==ex[8] for r in rows),('Native sleep contact missing',rows)
        else:
            assert max(r[4] for r in rows)>=20,('Rest contact/damage missing',rows[:30])
            active={r[1] for r in rows if r[2]}
            assert active=={1},('Rest source one-frame hit window',active)
            assert any(r[1]==29 and r[5]==ex[21] for r in rows), 'Rest startup intangibility missing'
            assert any(r[1]==30 and r[5]==ex[22] for r in rows), 'Rest intangibility did not expire'
            assert max(r[1] for r in rows)>=249, 'Rest donor sleep/recovery duration shortened'
        checks=['real special input','native sleep contact' if mode=='sing' else 'native Rest damage/contact','source duration and recovery']
        if mode=='rest':checks+=['one-frame source hitbox','original intangibility expiration']
    elif mode=='air-land':
        pulse(0x800);frames(6);pulse(0x40|(176<<24));frames(180)
        assert set(ex[16:18])<=seen,('Tornado air/ground transition missing',seen)
        checks=['aerial start','native landing transition retains donor','recovery on stage '+str(args.stage)]
    elif mode=='interrupt':
        pulse(0x40|(80<<24));frames(18)
        pulse(0x10);w32(e['native']['sSC1PTrainingModeMenu'],4);pulse(0x80);frames(90)
        assert u32(fighter()+0x24)<220,('Training reset retained special',seen)
        assert not list(weapons(14)), 'Training reset retained PK Thunder owner'
        checks=['real Training reset during special','weapon/context cleanup','running recreated fighter']
    keys(0);keys_port(1,0)
    wait(lambda:u32(fighter()+0x24)==10,'Edge-case native recovery',seconds=30)
    e['tracking']=False
    assert not seen.intersection((0,7,8,9)),('Edge-case KO/respawn instead of recovery',mode,seen)
    assert not u32(e['native']['__osFaultedThread']),e['diagnostic']()
    assert u32(fighter()+8)==args.body and not e['animation_errors'],e['diagnostic']()
    assert all(math.isfinite(v) and abs(v)<50000 for row in e['trace'] for v in row[2]), 'Invalid edge-case position'
    report=dict(rom_sha256=hashlib.sha256(e['rom']).hexdigest(),body=args.body,stage=args.stage,
                edge_case=mode,checks=checks,observed_statuses=sorted(seen),rendering='null')
    if fixture:report['stage_geometry_fixture']=fixture
    (e['report_directory']/f'cpu-scenes-edge-{mode}-{args.body}-{args.stage}.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: special edge case',report,flush=True)
