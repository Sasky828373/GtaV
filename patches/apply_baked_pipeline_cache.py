#!/usr/bin/env python3
from pathlib import Path
p=Path("src/native-renderer/src/native_renderer.cpp")
s=p.read_text()
old="static std::unordered_map<uint64_t,NativePipelineCacheEntry> pipelineCache;\nstatic std::mutex graphicsPipelineCreateMutex;"
new="static std::unordered_map<uint64_t,NativePipelineCacheEntry> pipelineCache;\nstatic std::unordered_map<uint64_t,VkPipeline> graphicsBakedPipelineCache;\nstatic std::mutex graphicsPipelineCreateMutex;"
assert old in s
s=s.replace(old,new,1)
old=""" VkGraphicsPipelineCreateInfo pci{VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO};pci.pNext=&rendering;pci.stageCount=2;pci.pStages=stages;pci.pVertexInputState=&vi;pci.pInputAssemblyState=&ia;pci.pViewportState=&vp;pci.pRasterizationState=&rs;pci.pMultisampleState=&ms;pci.pDepthStencilState=&ds;pci.pColorBlendState=&cb;pci.pDynamicState=&dyn;pci.layout=layout;
 VkPipeline pipe{};VkResult pr=VK_ERROR_INITIALIZATION_FAILED;
 {
   std::lock_guard<std::mutex> createLock(graphicsPipelineCreateMutex);
   char d[192];snprintf(d,sizeof(d),"attrs=%u bindings=%u colors=%u depthFmt=%d topology=%d",vaCount,vbCount,colorCount,(int)rendering.depthAttachmentFormat,(int)ia.topology);
   gtavdiag::checkpoint("native-pipeline-create-enter",d);
   pr=vkCreateGraphicsPipelines(g.device,VK_NULL_HANDLE,1,&pci,nullptr,&pipe);
   gtavdiag::checkpoint("native-pipeline-create-return");
 }
 if(pr!=VK_SUCCESS){char d[64];snprintf(d,sizeof(d),"vkResult=%d",(int)pr);gtavdiag::checkpoint("native-pipeline-create-failed",d);/* descriptor set reclaimed with owning pool at shutdown */vkDestroyPipelineLayout(g.device,layout,nullptr);vkDestroyDescriptorSetLayout(g.device,dsl,nullptr);return false;}
 if(!gtav_native_renderer_register_graphics_state(key,pipe,layout,desc)){vkDestroyPipeline(g.device,pipe,nullptr);/* descriptor set reclaimed with owning pool at shutdown */vkDestroyPipelineLayout(g.device,layout,nullptr);vkDestroyDescriptorSetLayout(g.device,dsl,nullptr);return false;}
"""
new=""" VkGraphicsPipelineCreateInfo pci{VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO};pci.pNext=&rendering;pci.stageCount=2;pci.pStages=stages;pci.pVertexInputState=&vi;pci.pInputAssemblyState=&ia;pci.pViewportState=&vp;pci.pRasterizationState=&rs;pci.pMultisampleState=&ms;pci.pDepthStencilState=&ds;pci.pColorBlendState=&cb;pci.pDynamicState=&dyn;pci.layout=layout;
 uint64_t bakedKey=0x4754415642414b45ull;
 auto hk=[&](uint64_t v){bakedKey=hashMix(bakedKey,v);};
 auto hbytes=[&](const void* ptr,size_t n){const uint8_t* b=(const uint8_t*)ptr;for(size_t i=0;i<n;i++)hk(b[i]);};
 hk((uintptr_t)vs);hk((uintptr_t)ps);
 hk(vaCount);for(uint32_t i=0;i<vaCount;i++)hbytes(&vaDesc[i],sizeof(vaDesc[i]));
 hk(vbCount);for(uint32_t i=0;i<vbCount;i++)hbytes(&vbDesc[i],sizeof(vbDesc[i]));
 hk((uint64_t)ia.topology);hbytes(&rs,sizeof(rs));
 hk((uint64_t)ms.rasterizationSamples);hk((uint64_t)compatSampleMask);hbytes(&ds,sizeof(ds));
 hk(colorCount);for(uint32_t i=0;i<colorCount;i++){hk((uint64_t)colorFormats[i]);hbytes(&cba[i],sizeof(cba[i]));}
 hk((uint64_t)rendering.depthAttachmentFormat);hk((uint64_t)rendering.stencilAttachmentFormat);
 hk((uint64_t)bindings.size());for(const auto& b:bindings){hk(b.binding);hk((uint64_t)b.descriptorType);hk(b.descriptorCount);hk(b.stageFlags);}
 hk(push.stageFlags);hk(push.offset);hk(push.size);
 VkPipeline pipe{};VkResult pr=VK_SUCCESS;
 {std::lock_guard<std::mutex> cacheLock(pipelineCacheMutex);auto it=graphicsBakedPipelineCache.find(bakedKey);if(it!=graphicsBakedPipelineCache.end())pipe=it->second;}
 if(pipe)gtavdiag::checkpoint("native-pipeline-baked-reused");
 else{
   std::lock_guard<std::mutex> createLock(graphicsPipelineCreateMutex);
   {std::lock_guard<std::mutex> cacheLock(pipelineCacheMutex);auto it=graphicsBakedPipelineCache.find(bakedKey);if(it!=graphicsBakedPipelineCache.end())pipe=it->second;}
   if(pipe)gtavdiag::checkpoint("native-pipeline-baked-reused-after-lock");
   else{
     char d[192];snprintf(d,sizeof(d),"attrs=%u bindings=%u colors=%u depthFmt=%d topology=%d",vaCount,vbCount,colorCount,(int)rendering.depthAttachmentFormat,(int)ia.topology);
     gtavdiag::checkpoint("native-pipeline-create-enter",d);
     pr=vkCreateGraphicsPipelines(g.device,VK_NULL_HANDLE,1,&pci,nullptr,&pipe);
     gtavdiag::checkpoint("native-pipeline-create-return");
     if(pr==VK_SUCCESS&&pipe){std::lock_guard<std::mutex> cacheLock(pipelineCacheMutex);graphicsBakedPipelineCache[bakedKey]=pipe;}
   }
 }
 if(pr!=VK_SUCCESS||!pipe){char d[64];snprintf(d,sizeof(d),"vkResult=%d",(int)pr);gtavdiag::checkpoint("native-pipeline-create-failed",d);vkDestroyPipelineLayout(g.device,layout,nullptr);vkDestroyDescriptorSetLayout(g.device,dsl,nullptr);return false;}
 if(!gtav_native_renderer_register_graphics_state(key,pipe,layout,desc)){vkDestroyPipelineLayout(g.device,layout,nullptr);vkDestroyDescriptorSetLayout(g.device,dsl,nullptr);return false;}
"""
assert old in s
s=s.replace(old,new,1)
old="{std::lock_guard<std::mutex> l(pipelineCacheMutex);pipelineCache.clear();}"
assert old in s
s=s.replace(old,"{std::lock_guard<std::mutex> l(pipelineCacheMutex);pipelineCache.clear();graphicsBakedPipelineCache.clear();}",1)
p.write_text(s)
print("Applied graphics-safe baked-state pipeline cache")
