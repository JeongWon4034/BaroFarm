package com.freshgrowth.comment;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CommentMapper {
    void insert(Comment comment);
    Comment findById(@Param("commentId") Long commentId);
    List<Comment> findByPostId(@Param("postId") Long postId);
    int update(@Param("commentId") Long commentId, @Param("authorId") Long authorId, @Param("content") String content);
    int delete(@Param("commentId") Long commentId, @Param("authorId") Long authorId);
}
