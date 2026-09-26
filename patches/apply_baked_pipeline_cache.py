#!/usr/bin/env python3
from pathlib import Path
p=Path("src/native-renderer/src/native_renderer.cpp")
s=p.read_text()

# Gold-safe strategy: do NOT share VkPipeline objects between different full draw states.
# Keep the original graphicsStateKey and registration/ownership behavior untouched.
# Only give the Vulkan driver a real VkPipelineCache, which can reuse internal compiled
# pipeline data without changing which VkPipeline/layout/state GTA receives.

old="static std::unordered_map<uint64_t,NativePipelineCacheEntry> pipelineCache;\nstatic std::mutex graphicsPipelineCreateMutex;"
new="static std::unordered_map<uint64_t,NativePipelineCacheEntry> pipelineCache;\nstatic VkPipelineCache driverGraphicsPipelineCache{};\nstatic std::mutex graphicsPipelineCreateMutex;"
assert old in s
s=s.replace(old,new,1)

old="""   pr=vkCreateGraphicsPipelines(g.device,VK_NULL_HANDLE,1,&pci,nullptr,&pipe);
   gtavdiag::checkpoint("native-pipeline-create-return");"""
new="""   if(!driverGraphicsPipelineCache){
     VkPipelineCacheCreateInfo pcci{VK_STRUCTURE_TYPE_PIPELINE_CACHE_CREATE_INFO};
     VkResult pcr=vkCreatePipelineCache(g.device,&pcci,nullptr,&driverGraphicsPipelineCache);
     char pcmsg[64];snprintf(pcmsg,sizeof(pcmsg),"vkResult=%d",(int)pcr);
     gtavdiag::checkpoint("native-driver-pipeline-cache-create",pcmsg);
   }
   pr=vkCreateGraphicsPipelines(g.device,driverGraphicsPipelineCache,1,&pci,nullptr,&pipe);
   gtavdiag::checkpoint("native-pipeline-create-return");"""
assert old in s
s=s.replace(old,new,1)

old="{std::lock_guard<std::mutex> l(pipelineCacheMutex);pipelineCache.clear();}"
new="{std::lock_guard<std::mutex> l(pipelineCacheMutex);pipelineCache.clear();}if(driverGraphicsPipelineCache&&g.device){vkDestroyPipelineCache(g.device,driverGraphicsPipelineCache,nullptr);driverGraphicsPipelineCache=VK_NULL_HANDLE;}"
assert old in s
s=s.replace(old,new,1)

p.write_text(s)
print("Applied Gold-safe driver VkPipelineCache; no cross-state VkPipeline sharing")
