package com.freshgrowth.user;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface UserMapper {
    void insert(User user);
    User findById(@Param("userId") Long userId);
    User findByEmail(@Param("email") String email);
    boolean existsByName(@Param("name") String name);
    int updateProfile(User user);
    int deactivate(@Param("userId") Long userId);
}
