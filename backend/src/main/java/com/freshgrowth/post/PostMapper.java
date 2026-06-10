package com.freshgrowth.post;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface PostMapper {
    void insert(Post post);
    Post findById(@Param("postId") Long postId);
    List<Post> findAll(@Param("offset") int offset, @Param("size") int size,
                       @Param("keyword") String keyword, @Param("sort") String sort);
    long countAll(@Param("keyword") String keyword);
    int update(Post post);
    int delete(@Param("postId") Long postId, @Param("authorId") Long authorId);
    int increaseView(@Param("postId") Long postId);
}
