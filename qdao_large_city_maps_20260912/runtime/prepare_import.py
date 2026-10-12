from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, uuid
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGE_REPO = ROOT.parent
CLIENT = IMAGE_REPO.parent / 'mmorpg-client'
RESOURCE_ROOT = 'Assets/Resources/World/FestivalRegions'
NAMESPACE = uuid.UUID('c036bdba-e617-4df1-962b-a2a5da79497e')
SPECS = [
    ('penglai', 'day', '蓬莱岛', 'penglai_island/penglai-island-native.png', 'penglai_island/penglai-island.prompt.txt'),
    ('penglai', 'festival', '蓬莱岛·中秋月夜', 'festival_variants/penglai_mid_autumn/map-native.png', 'festival_variants/penglai_mid_autumn/map.prompt.txt'),
    ('donghai', 'day', '东海渔村', 'donghai_fishing_village/donghai-fishing-village-native.png', 'donghai_fishing_village/donghai-fishing-village.prompt.txt'),
    ('donghai', 'festival', '东海渔村·元宵灯会', 'festival_variants/donghai_lantern_festival/map-native.png', 'festival_variants/donghai_lantern_festival/map.prompt.txt'),
    ('lanxian', 'day', '揽仙镇', 'lanxian_town/lanxian-town-native.png', 'lanxian_town/lanxian-town.prompt.txt'),
    ('lanxian', 'festival', '揽仙镇·春节', 'festival_variants/lanxian_spring_festival/map-native.png', 'festival_variants/lanxian_spring_festival/map.prompt.txt'),
]
META = '''fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 100
  spriteMode: 0
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: 100
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 0
  alphaUsage: 0
  alphaIsTransparency: 0
  spriteTessellationMethod: 0
  spriteTessellationDetail: -1
  spriteGeometrySubdivision: -1
  textureType: 0
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 100
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 4
    buildTarget: Standalone
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 100
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    customData:
    physicsShape: []
    bones: []
    spriteID:
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    spriteCustomMetadata:
      entries: []
    nameFileIdTable: {{}}
  mipmapLimitGroupName:
  pSDRemoveMatte: 0
  userData:
  assetBundleName:
  assetBundleVariant:
'''
FOLDER_META = '''fileFormatVersion: 2
guid: {guid}
folderAsset: yes
DefaultImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
'''

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', '-C', str(IMAGE_REPO), *args], text=True, encoding='utf-8').strip()

def guid(relative):
    return uuid.uuid5(NAMESPACE, relative.replace('\\', '/')).hex

def write_new_or_same(path, content, check):
    if path.exists():
        if path.read_text(encoding='utf-8').replace('\r\n', '\n') != content:
            raise RuntimeError(f'Existing metadata differs; preserve and inspect: {path}')
    elif check:
        raise RuntimeError(f'Missing metadata: {path}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8', newline='\n')

def main():
    parser = argparse.ArgumentParser(description='Copy six native map PNGs unchanged and validate Unity import contracts.')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    expectations = {}
    for manifest_path, prefix in [(ROOT/'manifest.json', ''), (ROOT/'festival_variants/manifest.json', 'festival_variants/')]:
        for entry in json.loads(manifest_path.read_text(encoding='utf-8-sig'))['maps']:
            expectations[prefix + entry['file']] = entry['sha256']
    artifacts = []
    for name in ['', '/penglai', '/donghai', '/lanxian']:
        relative = RESOURCE_ROOT + name
        folder = CLIENT/relative
        if not args.check:
            folder.mkdir(parents=True, exist_ok=True)
        write_new_or_same(Path(str(folder)+'.meta'), FOLDER_META.format(guid=guid(relative)), args.check)
    for region, atmosphere, name, source_relative, prompt_relative in SPECS:
        source = ROOT/source_relative
        assert source.exists() and (ROOT/prompt_relative).exists()
        source_hash = sha(source)
        assert source_hash == expectations[source_relative], source_relative
        with Image.open(source) as im:
            im.load()
            assert im.size == (1254,1254), (source_relative,im.size)
            size, mode = list(im.size), im.mode
        relative = f'{RESOURCE_ROOT}/{region}/{atmosphere}.png'
        destination = CLIENT/relative
        if args.check:
            assert destination.exists() and sha(destination) == source_hash, relative
        else:
            if destination.exists() and sha(destination) != source_hash:
                raise RuntimeError(f'Existing destination differs; preserve and inspect: {destination}')
            shutil.copyfile(source, destination)
        asset_guid = guid(relative)
        write_new_or_same(Path(str(destination)+'.meta'), META.format(guid=asset_guid), args.check)
        assert sha(destination) == source_hash
        with Image.open(destination) as im:
            im.load()
            assert im.size == (1254,1254)
        artifacts.append({
            'region':region, 'atmosphere':atmosphere, 'name':name,
            'source':source.relative_to(IMAGE_REPO).as_posix(),
            'source_prompt':(ROOT/prompt_relative).relative_to(IMAGE_REPO).as_posix(),
            'client_asset':relative,
            'resources_path':f'World/FestivalRegions/{region}/{atmosphere}',
            'native_size':size, 'imported_source_size':size, 'source_color_mode':mode,
            'source_sha256':source_hash, 'client_sha256':sha(destination),
            'source_and_client_bytes_identical':True,
            'native_no_upscale':True, 'crop':None, 'guid':asset_guid,
            'source_last_changed_commit':git('log','-1','--format=%H','--',source.relative_to(IMAGE_REPO).as_posix())
        })
    result = {
        'schema_version':1, 'status':'native_assets_prepared_and_verified',
        'scope':'Six native map resources; runtime scene, navigation and game-flow verification are tracked separately.',
        'source_image_repository_head':git('rev-parse','HEAD'),
        'rebuild_script':'qdao_large_city_maps_20260912/runtime/prepare_import.py',
        'verification_command':'python qdao_large_city_maps_20260912/runtime/prepare_import.py --check',
        'source_generation':'built-in image_gen; model/quality API flags were not exposed in the recorded generation tool',
        'style':'Original Q-style Daoist regional maps with Spring Festival, Lantern Festival and Mid-Autumn variants; the latest user instruction does not mandate jade/green/gold.',
        'import_settings':{
            'texture_type':'Default / Texture2D','max_texture_size':2048,'npot_scale':'None',
            'filter_mode':'Bilinear','wrap_mode':'Clamp','mipmaps':False,'compression':'None',
            'read_write_enabled':False,'srgb':True,'alpha_usage':'None',
            'stable_guid_strategy':'UUIDv5 over repository-relative asset path with fixed namespace'
        },
        'resolution_limits':{
            'native_pixels_per_side':1254, 'painted_world_units_per_side':300,
            'native_pixels_per_world_unit':4.18,
            'note':'The complete native 1254 x 1254 image is displayed over a 300 x 300 world area. Close camera views magnify native artwork and can be soft. No extra detail or native 4K/6K is claimed; independently regenerated high-detail tiles are not part of these six imports.'
        },
        'checks':{'png_decode':6,'dimensions_1254_square':6,'source_manifest_hashes':6,'client_source_byte_equality':6,'texture_metadata_contract':6,'folder_metadata':4,'passed':True},
        'maps':artifacts
    }
    if not args.check:
        encoded = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
        (ROOT/'runtime/import-manifest.json').write_text(encoded, encoding='utf-8', newline='\n')
        doc = CLIENT/'Docs/ArtEvidence/festival-regions-import.json'
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text(encoded, encoding='utf-8', newline='\n')
    else:
        left = json.loads((ROOT/'runtime/import-manifest.json').read_text(encoding='utf-8'))
        right = json.loads((CLIENT/'Docs/ArtEvidence/festival-regions-import.json').read_text(encoding='utf-8'))
        assert left == right, 'Client and image import manifests differ'
        for now, recorded in zip(artifacts, left['maps']):
            assert now == recorded, f'Import mapping changed: {now["client_asset"]}'
    print(json.dumps({'passed':True, 'maps':len(artifacts), 'mode':'check' if args.check else 'prepare', 'native_dimensions':[1254,1254], 'client_resources':RESOURCE_ROOT}, ensure_ascii=False))

if __name__ == '__main__':
    main()