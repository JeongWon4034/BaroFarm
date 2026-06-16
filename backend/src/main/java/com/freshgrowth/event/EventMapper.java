package com.freshgrowth.event;

import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface EventMapper {
    int insert(BehaviorEvent event);
}
